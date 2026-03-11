from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from .models import Interview, Patient, Interviewer, InterviewState
from .OllamaLLM import CHANGE_SETTINGS
import json
import time
from . import autogenerate_profile
from . import autogenerate_state
# TODO REFACTOR FOR autogenerate.py

from .OllamaLLM.Patient import response as patient_response

# ==============================================================================
# 1. LLM CALLS
# ==============================================================================

def getResponsePatient(interview, user_input, tone='neutral', user_id=None):
    """Generate the patient's reply. Replace dummy logic with LLM call."""
    return patient_response.response(interview.id,
                                     {"content": user_input, "tone": tone}, user_id=user_id)
    
    
def process_settings(interview, settings: dict) -> dict:
    """Save settings to the ChatSettings model for this interview."""
    return CHANGE_SETTINGS.save_chat_settings(interview, settings)


@login_required(login_url='login')
def autogenerate_question(request, interview_id):
    """Generate a suggested interviewer question. Replace dummy logic with LLM call."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    get_object_or_404(Interview, id=interview_id, createdBy=request.user)
    # TODO: build context from interview history and call LLM
    time.sleep(3)
    return JsonResponse({'question': 'SAMPLE QUESTION'})


@login_required(login_url='login')
def generate_field(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    data         = json.loads(request.body)
    field        = data.get('field', '')
    deps         = data.get('dependencies', {})
    instructions = data.get('instructions', '')
    ns_settings  = CHANGE_SETTINGS.get_new_session_settings(request.user)
    ns_settings  = CHANGE_SETTINGS.new_session_settings_as_dict(ns_settings)
    return JsonResponse({'value': autogenerate_profile.generateField(field, deps, instructions, request, settings=ns_settings)})


@login_required(login_url='login')
def populate_state(request, interview_id):
    """Dummy endpoint: populates InterviewState fields one by one with 1s delay each.
    Streams JSON events so the frontend can update fields as they arrive."""
    import django.http
    interview = get_object_or_404(Interview, id=interview_id, createdBy=request.user)
    state     = getattr(interview, 'state', None)
    if not state:
        return JsonResponse({'error': 'No state found'}, status=404)

    fields        = ['summary', 'notes', 'patient_summary', 'patient_feelings', 'patient_behavior']
    chat_settings = CHANGE_SETTINGS.get_chat_settings(interview)

    def stream():
        for field in fields:
            resp = autogenerate_state.response(field, state, settings=chat_settings)
            setattr(state, field, resp)
            state.save(update_fields=[field])
            yield f"data: {json.dumps({'field': field, 'value': resp})}\n\n"
        yield 'data: {"done": true}\n\n'

    return django.http.StreamingHttpResponse(stream(), content_type='text/event-stream')


# ==============================================================================
# 2. OTHER NEW SESSION RELATED
# ==============================================================================

@login_required(login_url='login')
def default_settings(request):
    """GET: return current generation settings. POST: update them."""
    if request.method == 'POST':
        data = json.loads(request.body)
        sid  = data.get('settings_id', 'generation')
        if sid == 'generation':
            result = CHANGE_SETTINGS.save_new_session_settings(request.user, data)
            return JsonResponse({'ok': True, 'settings_id': sid, **result})
        return JsonResponse({'ok': True, 'settings_id': sid})
    ns = CHANGE_SETTINGS.get_new_session_settings(request.user)
    return JsonResponse(CHANGE_SETTINGS.new_session_settings_as_dict(ns))


@login_required(login_url='login')
def patient_list(request):
    """Returns all patients as JSON — supports my_patients and psi filters"""
    only_mine = request.GET.get('mine') == '1'
    only_psi  = request.GET.get('psi')  == '1'
    qs = Patient.objects.all()
    if only_mine:
        qs = qs.filter(createdBy=request.user)
    if only_psi:
        qs = qs.filter(patient_psi=True)
    qs = qs.order_by('-createdAt')
    data = [{
        'id':              p.id,
        'name':            p.name            or '',
        'age':             p.age             or '',
        'gender':          p.gender          or '',
        'disorder':        p.disorder        or '',
        'profile_summary': p.profile_summary or '',
        'patient_psi':     p.patient_psi,
        'is_mine':         p.createdBy == request.user,
        'createdBy':       p.createdBy.username if p.createdBy else '—',
        'createdAt':       p.createdAt.strftime('%Y-%m-%d') if p.createdAt else '',
    } for p in qs]
    return JsonResponse({'patients': data})


@login_required(login_url='login')
def patient_detail(request, patient_id):
    p = get_object_or_404(Patient, id=patient_id)
    return JsonResponse({
        'id':                   p.id,
        'name':                 p.name,
        'age':                  p.age,
        'gender':               p.gender,
        'ethnicity':            p.ethnicity,
        'marital_status':       p.marital_status,
        'education':            p.education,
        'occupation':           p.occupation,
        'disorder':             p.disorder,
        'type':                 p.type,
        'base_emotions':        p.base_emotions,
        'childhood_history':    p.childhood_history,
        'education_history':    p.education_history,
        'occupation_history':   p.occupation_history,
        'relationship_history': p.relationship_history,
        'medical_history':      p.medical_history,
        'personal_history':     p.personal_history,
        'session_history':      p.session_history,
        'helpless_beliefs':     p.helpless_beliefs,
        'unlovable_beliefs':    p.unlovable_beliefs,
        'worthless_beliefs':    p.worthless_beliefs,
        'intermediate_belief':  p.intermediate_belief,
        'coping_strategies':    p.coping_strategies,
        'trigger':              p.trigger,
        'auto_thoughts':        p.auto_thoughts,
        'behavior':             p.behavior,
        'intake':               p.intake,
        'vignette':             p.vignette,
        'family_tree':          p.family_tree,
        'timeline':             p.timeline,
        'createdBy':            p.createdBy.username if p.createdBy else '—',
        'createdAt':            p.createdAt.strftime('%Y-%m-%d') if p.createdAt else '',
        'patient_psi':          p.patient_psi,
    })


# ==============================================================================
# 3. CREATE SESSION
# ==============================================================================

@login_required(login_url='login')
def new_interview(request):
    if request.method == 'POST':
        d = request.POST

        def to_list(val):
            """Convert comma-separated string to list, stripping whitespace"""
            return [x.strip() for x in val.split(',') if x.strip()] if val else []

        patient = Patient.objects.create(
            createdBy            = request.user,
            name                 = d.get('name', ''),
            age                  = int(d['age']) if d.get('age') else None,
            gender               = d.get('gender', ''),
            ethnicity            = d.get('ethnicity', ''),
            marital_status       = d.get('marital_status', ''),
            education            = d.get('education', ''),
            occupation           = d.get('occupation', ''),
            disorder             = d.get('disorder', ''),
            type                 = to_list(d.get('type', '')),
            base_emotions        = to_list(d.get('base_emotions', '')),
            helpless_beliefs     = to_list(d.get('helpless_beliefs', '')),
            unlovable_beliefs    = to_list(d.get('unlovable_beliefs', '')),
            worthless_beliefs    = to_list(d.get('worthless_beliefs', '')),
            intermediate_belief  = d.get('intermediate_belief', ''),
            trigger              = d.get('trigger', ''),
            auto_thoughts        = d.get('auto_thoughts', ''),
            coping_strategies    = d.get('coping_strategies', ''),
            behavior             = d.get('behavior', ''),
            intake               = d.get('intake', ''),
            vignette             = d.get('vignette', ''),
            childhood_history    = d.get('childhood_history', ''),
            education_history    = d.get('education_history', ''),
            occupation_history   = d.get('occupation_history', ''),
            relationship_history = d.get('relationship_history', ''),
            medical_history      = d.get('medical_history', ''),
            personal_history     = d.get('personal_history', ''),
            session_history      = d.get('session_history', ''),
            family_tree          = d.get('family_tree', ''),
            timeline             = d.get('timeline', ''),
            patient_psi          = d.get('patient_psi', 'False') == 'True',
        )

        interview = Interview.objects.create(
            createdBy = request.user,
            patient   = patient,
            title     = d.get('title') or f"Session #{Interview.objects.count() + 1}",
        )

        Interviewer.objects.create(interview=interview)
        InterviewState.objects.create(interview=interview)

        # Seed ChatSettings from NewSessionSettings (all four fields) then clear
        ns = CHANGE_SETTINGS.get_new_session_settings(request.user)
        CHANGE_SETTINGS.seed_chat_settings(interview, ns)
        CHANGE_SETTINGS.delete_new_session_settings(request.user)
        
        patient.profile_summary = autogenerate_profile.generateField('profile_summary', {}, '', request, settings=patient.vignette)
        patient.save(update_fields=['profile_summary'])

        return redirect(f"/chat/load/{interview.id}/?new=1")
    return render(request, 'chat/new_interview.html')


@login_required(login_url='login')
def new_interview_from_patient(request):
    """Creates a new session from an existing patient (no duplicate patient created)."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    data       = json.loads(request.body)
    patient_id = data.get('patient_id')
    patient    = get_object_or_404(Patient, id=patient_id)

    interview = Interview.objects.create(
        createdBy = request.user,
        patient   = patient,
        title     = f"Session #{Interview.objects.count() + 1}",
    )
    Interviewer.objects.create(interview=interview)
    InterviewState.objects.create(interview=interview)

    # Seed ChatSettings from NewSessionSettings (all four fields) then clear
    ns = CHANGE_SETTINGS.get_new_session_settings(request.user)
    CHANGE_SETTINGS.seed_chat_settings(interview, ns)
    CHANGE_SETTINGS.delete_new_session_settings(request.user)

    return JsonResponse({'redirect': f'/chat/load/{interview.id}/?new=1'})


# ==============================================================================
# 4. LIST SESSIONS
# ==============================================================================

@login_required(login_url='login')
def load_list(request):
    return render(request, 'chat/load_list.html')


@login_required(login_url='login')
def interview_list_api(request):
    """Returns interviews as JSON with filters"""
    only_mine     = request.GET.get('mine')     == '1'
    show_archived = request.GET.get('archived') == '1'

    qs = Interview.objects.select_related('patient', 'createdBy', 'state')

    if not show_archived:
        qs = qs.filter(archived=False)
    if only_mine:
        qs = qs.filter(createdBy=request.user)

    qs = qs.order_by('-createdAt')

    data = [{
        'id':           i.id,
        'title':        i.title or f'Interview #{i.id}',
        'createdBy':    i.createdBy.username if i.createdBy else '—',
        'is_mine':      i.createdBy == request.user,
        'patient_name': i.patient.name if i.patient else '—',
        'patient_psi':  i.patient.patient_psi if i.patient else False,
        'disorder':     i.patient.disorder if i.patient else '—',
        'turn_count':   getattr(getattr(i, 'state', None), 'turn_count', 0),
        'createdAt':    i.createdAt.strftime('%Y-%m-%d %H:%M'),
        'updated_at':   i.updated_at.strftime('%Y-%m-%d %H:%M'),
        'archived':     i.archived,
        'patient_id':   i.patient.id if i.patient else None,
    } for i in qs]

    return JsonResponse({'interviews': data})


@login_required(login_url='login')
def interview_messages_preview(request, interview_id):
    """Returns last 5 messages for preview modal"""
    interview = get_object_or_404(Interview, id=interview_id)
    messages  = interview.messages.order_by('-timestamp')[:5]
    data = [{
        'role':      m.role,
        'content':   m.content,
        'timestamp': m.timestamp.strftime('%H:%M'),
    } for m in reversed(list(messages))]
    return JsonResponse({'messages': data, 'total': interview.messages.count()})


@login_required(login_url='login')
def archive_interview(request, interview_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    interview = get_object_or_404(Interview, id=interview_id)
    if interview.createdBy != request.user and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    interview.archived = not interview.archived  # toggle
    interview.save()
    return JsonResponse({'archived': interview.archived})


@login_required(login_url='login')
def delete_interview(request, interview_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    interview = get_object_or_404(Interview, id=interview_id)
    if interview.createdBy != request.user and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    patient = interview.patient
    interview.delete()
    if patient and not patient.patient_psi:
        patient.delete()
    return JsonResponse({'deleted': True})


@login_required(login_url='login')
def download_transcript(request, interview_id):
    """Download the interview transcript as TXT or JSON."""
    import json as _json
    from django.http import HttpResponse

    interview = get_object_or_404(Interview, id=interview_id, createdBy=request.user)
    fmt       = request.GET.get('format', 'txt').lower()
    messages  = interview.messages.order_by('timestamp')
    state     = getattr(interview, 'state', None)

    meta = {
        'id':        interview.id,
        'title':     interview.title or f'Interview #{interview.id}',
        'user':      interview.createdBy.username if interview.createdBy else '—',
        'createdAt': interview.createdAt.strftime('%Y-%m-%d %H:%M:%S'),
        'turns':     getattr(state, 'turn_count', 0),
        'patient':   interview.patient.name if interview.patient else '—',
        'disorder':  interview.patient.disorder if interview.patient else '—',
    }

    if fmt == 'json':
        payload = {
            'system': meta,
            'messages': [
                {
                    'id':        m.id,
                    'role':      m.role,
                    'content':   m.content,
                    'tone':      m.tone or '',
                    'behavior':  m.behavior or '',
                    'timestamp': m.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                }
                for m in messages
            ],
        }
        response = HttpResponse(
            _json.dumps(payload, indent=2),
            content_type='application/json',
        )
        filename = f"transcript_{interview.id}.json"
    else:
        lines = [
            f"system: id={meta['id']}",
            f"system: title={meta['title']}",
            f"system: user={meta['user']}",
            f"system: createdAt={meta['createdAt']}",
            f"system: turns={meta['turns']}",
            f"system: patient={meta['patient']}",
            f"system: disorder={meta['disorder']}",
            '',
        ]
        for m in messages:
            tone_suffix = f"  [{m.tone}]" if m.tone else ""
            behavior_suffix = f"  [Behavior: {m.behavior}]" if m.behavior else ""
            lines.append(f"{m.role}{tone_suffix}{behavior_suffix}: {m.content}")
            lines.append('')
        response = HttpResponse('\n'.join(lines), content_type='text/plain; charset=utf-8')
        filename = f"transcript_{interview.id}.txt"

    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# ==============================================================================
# 5. CHAT
# ==============================================================================

@login_required(login_url='login')
def load_interview(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id)
    patient   = interview.patient
    state     = getattr(interview, 'state', None)
    is_new    = request.GET.get('new') == '1'
    return render(request, 'chat/load_interview.html', {
        'interview': interview,
        'patient':   patient,
        'state':     state,
        'is_new':    is_new,
    })


@login_required(login_url='login')
def chat_view(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id, createdBy=request.user)
    messages  = interview.messages.all()
    interview.is_active = True
    interview.save()
    chat_settings = CHANGE_SETTINGS.get_chat_settings(interview)
    return render(request, 'chat/chat.html', {
        'interview':     interview,
        'messages':      messages,
        'chat_settings': chat_settings,
    })


@login_required(login_url='login')
def send_message(request, interview_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    interview  = get_object_or_404(Interview, id=interview_id, createdBy=request.user)
    user_input = request.POST.get('message', '').strip()
    tone       = request.POST.get('tone', 'neutral')
    if not user_input:
        return JsonResponse({'error': 'Empty message'}, status=400)    

    # Get patient response (LLM call — replace dummy logic here)
    reply = getResponsePatient(interview, user_input, tone, request.user.username)

    state = interview.state
    state.turn_count += 1
    state.save(update_fields=['turn_count'])

    return JsonResponse({'response': reply.get('content', ''), 'message_id': reply["id"], 'tone': reply.get('tone', 'neutral'), 'behavior': reply.get('behavior', '')})


@login_required(login_url='login')
def update_settings(request, interview_id):
    """Save chat generation settings for this interview."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    interview = get_object_or_404(Interview, id=interview_id, createdBy=request.user)
    data      = json.loads(request.body)
    result    = process_settings(interview, data)
    return JsonResponse({'ok': True, **result})


@login_required(login_url='login')
def save_notes(request, interview_id):
    """Auto-save interviewer notes."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    interview   = get_object_or_404(Interview, id=interview_id, createdBy=request.user)
    data        = json.loads(request.body)
    notes       = data.get('notes', '')
    interviewer = interview.interviewer
    interviewer.notes = notes
    interviewer.save(update_fields=['notes'])
    return JsonResponse({'ok': True})


@login_required(login_url='login')
def rate_message(request, interview_id, message_id):
    """Save a star rating (0–5, 0.5 increments) for a patient message."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    get_object_or_404(Interview, id=interview_id, createdBy=request.user)
    from .models import Message
    message = get_object_or_404(Message, id=message_id, interview_id=interview_id, role='patient')
    data   = json.loads(request.body)
    rating = data.get('rating')  # None means clear; otherwise 0–5 in 0.5 steps from UI
    if rating is None:
        message.rating = None
    else:
        try:
            rating = float(rating)
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid rating'}, status=400)
        # Round to nearest 0.5 star and clamp 0–5, then convert to 0–1 for storage
        rating = round(round(rating * 2) / 2, 1)
        rating = max(0.0, min(5.0, rating))
        message.rating = round(rating / 5, 2)
    message.save(update_fields=['rating'])
    # Return the 0–5 display value back to JS
    display_rating = round(float(message.rating) * 5, 1) if message.rating is not None else None
    return JsonResponse({'ok': True, 'rating': display_rating})


@login_required(login_url='login')
def end_interview(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id, createdBy=request.user)
    interview.is_active = False
    interview.save()
    return redirect('load_user')
