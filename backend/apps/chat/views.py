from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from .models import Interview, Patient, Interviewer, InterviewState
import json
import time
from . import autogenerate
# TODO REFACTOR FOR autogenerate.py

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

    return JsonResponse({'redirect': f'/chat/load/{interview.id}/?new=1'})

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
def populate_state(request, interview_id):
    """Dummy endpoint: populates InterviewState fields one by one with 1s delay each.
    Streams JSON events so the frontend can update fields as they arrive."""
    import django.http
    interview = get_object_or_404(Interview, id=interview_id, createdBy=request.user)
    state     = getattr(interview, 'state', None)
    if not state:
        return JsonResponse({'error': 'No state found'}, status=404)

    fields = ['summary', 'notes', 'patient_summary', 'patient_feelings', 'patient_behavior']

    def stream():
        for field in fields:
            time.sleep(1)
            setattr(state, field, 'TEST 5 SECONDS')
            state.save(update_fields=[field])
            yield f"data: {json.dumps({'field': field, 'value': 'TEST 5 SECONDS'})}\n\n"
        yield "data: {\"done\": true}\n\n"

    return django.http.StreamingHttpResponse(stream(), content_type='text/event-stream')


@login_required(login_url='login')
def chat_view(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id, createdBy=request.user)
    messages  = interview.messages.all()
    interview.is_active = True
    interview.save()
    return render(request, 'chat/chat.html', {
        'interview': interview,
        'messages':  messages,
    })


@login_required(login_url='login')
def send_message(request, interview_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    interview  = get_object_or_404(Interview, id=interview_id, createdBy=request.user)
    user_input = request.POST.get('message', '').strip()
    if not user_input:
        return JsonResponse({'error': 'Empty message'}, status=400)
    interview.messages.create(role='user', content=user_input)
    reply = 'LLM response placeholder'
    interview.messages.create(role='assistant', content=reply)
    interview.state.turn_count += 1
    interview.state.save()
    return JsonResponse({'response': reply})


@login_required(login_url='login')
def end_interview(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id, createdBy=request.user)
    interview.is_active = False
    interview.save()
    return redirect('load_user')


@login_required(login_url='login')
def generate_field(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    data  = json.loads(request.body)
    field = data.get('field', '')
    deps  = data.get('dependencies', {})
    
    return JsonResponse({'value': autogenerate.generateField(field, deps)})



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
        'id':          p.id,
        'name':        p.name        or '',
        'age':         p.age         or '',
        'gender':      p.gender      or '',
        'disorder':    p.disorder    or '',
        'profile_summary': p.profile_summary or '',
        'patient_psi': p.patient_psi,
        'is_mine':     p.createdBy == request.user,
        'createdBy':   p.createdBy.username if p.createdBy else '—',
        'createdAt':   p.createdAt.strftime('%Y-%m-%d') if p.createdAt else '',
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


@login_required(login_url='login')
def load_list(request):
    return render(request, 'chat/load_list.html')


@login_required(login_url='login')
def interview_list_api(request):
    """Returns interviews as JSON with filters"""
    only_mine    = request.GET.get('mine') == '1'
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
    interview.archived = not interview.archived   # toggle
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
    # Delete the interview (cascades to Messages, InterviewState, Interviewer)
    interview.delete()
    # Only delete the patient if it exists and is NOT a PSI dataset patient
    if patient and not patient.patient_psi:
        patient.delete()
    return JsonResponse({'deleted': True})
