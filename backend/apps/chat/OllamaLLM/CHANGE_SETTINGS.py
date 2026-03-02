"""
CHANGE_SETTINGS.py — Central hub for all settings operations.

All reads and writes for NewSessionSettings and ChatSettings flow through here.
Views should import and call these functions rather than touching the models directly.
"""

from . import DEFAULT_SETTINGS


# ---------------------------------------------------------------------------
# NewSessionSettings helpers  (generation / profile-autofill page)
# ---------------------------------------------------------------------------

def get_new_session_settings(user):
    """
    Return the NewSessionSettings row for *user*, creating one with defaults
    if it does not exist yet.
    """
    from apps.chat.models import NewSessionSettings
    ns, _ = NewSessionSettings.objects.get_or_create(
        user=user,
        defaults={
            'model':       DEFAULT_SETTINGS.GENERATION_MODEL,
            'temperature': DEFAULT_SETTINGS.GENERATION['temperature'],
        },
    )
    return ns


def save_new_session_settings(user, data: dict) -> dict:
    """
    Persist generation settings for *user*.

    Accepted keys in *data*: 'model', 'temperature'.
    Returns a dict suitable for passing straight back as a JsonResponse.
    """
    ns = get_new_session_settings(user)
    if 'temperature' in data:
        ns.temperature = float(data['temperature'])
    if 'model' in data:
        ns.model = data['model']
    ns.save()
    return {'model': ns.model, 'temperature': ns.temperature}


def delete_new_session_settings(user):
    """Delete the NewSessionSettings row for *user* (called when a session starts)."""
    from apps.chat.models import NewSessionSettings
    NewSessionSettings.objects.filter(user=user).delete()


def new_session_settings_as_dict(ns) -> dict:
    """Serialise a NewSessionSettings instance to a plain dict."""
    return {
        'model':       ns.model,
        'temperature': ns.temperature,
    }


# ---------------------------------------------------------------------------
# ChatSettings helpers  (in-session patient / interviewer settings)
# ---------------------------------------------------------------------------

def seed_chat_settings(interview, ns):
    """
    Create the ChatSettings row for *interview* seeded from a NewSessionSettings
    instance *ns*.  The model is taken from the new-session page; temperatures
    use their own role-specific defaults (patient: 0.7, interviewer: 0.3).

    Should be called exactly once, right after the Interview is created.
    """
    from apps.chat.models import ChatSettings
    cs, _ = ChatSettings.objects.get_or_create(
        interview=interview,
        defaults={
            'patient_model':           ns.model,
            'patient_temperature':     DEFAULT_SETTINGS.PATIENT['temperature'],
            'interviewer_model':       ns.model,
            'interviewer_temperature': DEFAULT_SETTINGS.INTERVIEWER['temperature'],
        },
    )
    return cs


def get_chat_settings(interview):
    """
    Return the ChatSettings row for *interview*, creating one with defaults
    if it does not exist yet.  Prefer calling seed_chat_settings() at session
    creation time so the row already exists with the right values.
    """
    from apps.chat.models import ChatSettings
    cs, _ = ChatSettings.objects.get_or_create(
        interview=interview,
        defaults={
            'patient_model':           DEFAULT_SETTINGS.PATIENT_MODEL,
            'patient_temperature':     DEFAULT_SETTINGS.PATIENT['temperature'],
            'interviewer_model':       DEFAULT_SETTINGS.INTERVIEWER_MODEL,
            'interviewer_temperature': DEFAULT_SETTINGS.INTERVIEWER['temperature'],
        },
    )
    return cs


def save_chat_settings(interview, data: dict) -> dict:
    """
    Persist patient or interviewer settings for *interview*.

    *data* must include 'settings_id': 'patient' | 'interviewer'.
    Accepted keys: 'model', 'temperature'.
    Returns {'settings_id': <sid>}.
    """
    cs  = get_chat_settings(interview)
    sid = data.get('settings_id', 'patient')

    if sid == 'patient':
        if 'temperature' in data:
            cs.patient_temperature = float(data['temperature'])
        if 'model' in data:
            cs.patient_model = data['model']
    elif sid == 'interviewer':
        if 'temperature' in data:
            cs.interviewer_temperature = float(data['temperature'])
        if 'model' in data:
            cs.interviewer_model = data['model']

    cs.save()
    return {'settings_id': sid}


def chat_settings_as_dict(cs) -> dict:
    """Serialise a ChatSettings instance to a plain dict."""
    return {
        'patient_model':           cs.patient_model,
        'patient_temperature':     cs.patient_temperature,
        'interviewer_model':       cs.interviewer_model,
        'interviewer_temperature': cs.interviewer_temperature,
    }
