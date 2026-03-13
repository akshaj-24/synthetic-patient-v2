from ...models import Interview, Patient, Message, ChatSettings, InterviewState as State
from langfuse import observe, get_client
langfuse = get_client()
# Prompt imports



# LLM response import
from .. import LLM_CALL as LLM

@observe()
def response(interview_id, question, user_id=None, feedback=None):
    
    interview = Interview.objects.get(id=interview_id)
    patient = interview.patient
    state = interview.state
    chatSettings = interview.chatSettings
    
    checkAndUpdateSummary(interview)
    
    call_args = getArgs(interview, patient, state)
    # Patient response workflow
    user_input = question["content"]
    user_tone = question["tone"]
    call_args["interviewer_question"] = user_input
    call_args["interviewer_tone"] = user_tone
    
    if feedback is not None:
        call_args["feedback"] = feedback
    elif feedback is None:
        call_args["feedback"] = "NULL"
    
    sys = langfuse.get_prompt("response/sys/tone_feelings_behavior", label="production")
    sys = sys.compile(**call_args)
    user = langfuse.get_prompt("response/user/tone_feelings_behavior", label="production")
    user = user.compile(**call_args)
    
    feelings_behavior_resp = LLM.call(
        id="patient_tone_feelings_behavior", 
        interview=interview,
        sys=sys,
        user=user,
        settings=None,
        metadata=None,
        metadata_fields=None,
        tools=True,)
    
    patient_feelings = feelings_behavior_resp.feelings
    patient_behavior = feelings_behavior_resp.behavior
    patient_tone = feelings_behavior_resp.tone
    
    call_args["patient_feelings"] = patient_feelings
    call_args["patient_behavior"] = patient_behavior
    call_args["patient_tone"] = patient_tone
    
    # # Get resp content 
    sys = langfuse.get_prompt("response/sys/response", label="production")
    sys = sys.compile(**call_args)
    user = langfuse.get_prompt("response/user/response", label="production")
    user = user.compile(**call_args)
    
    resp = LLM.call(
        id="patient_content", 
        interview=interview,
        sys=sys,
        user=user,
        settings=None,
        metadata=None,
        metadata_fields=None,
        tools=True,)
    
    content = resp.content
    
    call_args["patient_content_initial"] = content
    call_args["patient_feelings_initial"] = patient_feelings
    call_args["patient_behavior_initial"] = patient_behavior
    call_args["patient_tone_initial"] = patient_tone
    
    sys = langfuse.get_prompt("response/sys/grader", label="production")
    sys = sys.compile(**call_args)
    user = langfuse.get_prompt("response/user/grader", label="production")
    user = user.compile(**call_args)
    
    grader_resp = LLM.call(
        id="patient_grader", 
        interview=interview,
        sys=sys,
        user=user,
        settings=None,
        metadata=None,
        metadata_fields=None,
        tools=True,)
    
    change = grader_resp.change
    if change.lower() in ["true", "1", "yes"]:
        call_args["change"] = change
        call_args["feedback"] = grader_resp.feedback
        return response(interview_id, question, user_id, feedback)  # Recursive retry if grader indicates change needed
        
    call_args["change"] = change
    call_args["patient_content_final"] = content
    call_args["patient_feelings_final"] = patient_feelings
    call_args["patient_behavior_final"] = patient_behavior
    call_args["patient_tone_final"] = patient_tone
    
    response = {
        "content": content,
        "tone": patient_tone,
        "behavior": patient_behavior,
        "id": None,
    }
    
    # Persist user message (store tone so it appears in transcripts)
    interview.messages.create(role='user', content=user_input, tone=patient_tone)

    # Persist patient reply
    patient_msg = interview.messages.create(role='patient', content=content, tone=patient_tone, behavior=patient_behavior)
    
    state.turn_count += 1
    state.save(update_fields=['turn_count'])
    
    langfuse.update_current_trace(
        metadata={
            **call_args,  # all patient + state fields at time of response
            "response_turn":     state.turn_count,
            "response_length":   len(resp) if resp else 0,
            "message_id":        patient_msg.id,
        }
    )
    
    response["id"] = patient_msg.id

    return response


def checkAndUpdateSummary(interview):
    state = interview.state
    if state.turn_count >= state.summary_freq + state.summary_turn:  
        # UPDATE SUMMARY
        state.summary_turn = state.turn_count
        state.save(update_fields=['summary_turn'])
        
        call_args = {
            "last_N_turns": getLastNTurnsString(interview, n=state.summary_freq),
        }
        
        sys = langfuse.get_prompt("summary/sys/interview", label="production")
        sys = sys.compile(**call_args)
        user = langfuse.get_prompt("summary/user/interview", label="production")
        user = user.compile(**call_args)
    
        summary_resp = LLM.call(
            id="patient_grader", 
            interview=interview,
            sys=sys,
            user=user,
            settings=None,
            metadata=None,
            metadata_fields=None,
            tools=True,)
        
        updated_summary = summary_resp.summary
        state.summary = state.summary + "\n" + updated_summary
        state.save(update_fields=['summary'])
        
        call_args["latest_summary"] = updated_summary
        
        sys = langfuse.get_prompt("summary/sys/patient", label="production")
        sys = sys.compile(**call_args)
        user = langfuse.get_prompt("summary/user/patient", label="production")
        user = user.compile(**call_args)
        
        summary_resp = LLM.call(
            id="patient_grader", 
            interview=interview,
            sys=sys,
            user=user,
            settings=None,
            metadata=None,
            metadata_fields=None,
            tools=True,)
        
        updated_patient_summary = summary_resp.summary
        state.patient_summary = state.patient_summary + "\n" + updated_patient_summary
        state.save(update_fields=['patient_summary'])
        
    return 1        
        
# ----------------- HELPERS ----------------------------

def getLastNTurnsString(interview, n=5):
    messages = interview.messages.order_by('-timestamp')[:(n*2)][::-1]
    return "\n".join(
        f"{msg.role}:{msg.content} in tone {msg.tone} with behavior {msg.behavior if msg.behavior else 'N/A'}" for msg in messages
        )
    
def getLastNTurnsList(interview, n=5):
    messages = interview.messages.order_by('-timestamp')[:(n*2)][::-1]
    return [
        f"{msg.role}:{msg.content} in tone {msg.tone} with behavior {msg.behavior if msg.behavior else 'N/A'}" for msg in messages
        ]


def getArgs(interview, patient, state):
    return {
        # Patient fields
        "patient_name": patient.name,
        "patient_age": patient.age,
        "patient_gender": patient.gender,
        "patient_ethnicity": patient.ethnicity,
        "patient_education": patient.education,
        "patient_occupation": patient.occupation,
        "patient_disorder": patient.disorder,
        "patient_type": patient.type,
        "patient_marital_status": patient.marital_status,
        "patient_children": patient.children,
        "patient_grandchildren": patient.grandchildren,
        "patient_canonical_facts": patient.canonical_facts,
        "patient_childhood_history": patient.childhood_history,
        "patient_education_history": patient.education_history,
        "patient_occupation_history": patient.occupation_history,
        "patient_relationship_history": patient.relationship_history,
        "patient_medical_history": patient.medical_history,
        "patient_personal_history": patient.personal_history,
        "patient_session_history": patient.session_history,
        "patient_helpless_beliefs": patient.helpless_beliefs,
        "patient_unlovable_beliefs": patient.unlovable_beliefs,
        "patient_worthless_beliefs": patient.worthless_beliefs,
        "patient_intermediate_belief": patient.intermediate_belief,
        "patient_coping_strategies": patient.coping_strategies,
        "patient_trigger": patient.trigger,
        "patient_auto_thoughts": patient.auto_thoughts,
        "patient_base_emotions": patient.base_emotions,
        "patient_behavior": patient.behavior,
        "patient_impact": patient.impact,
        "patient_intake": patient.intake,
        "patient_vignette": patient.vignette,
        "patient_family_tree": patient.family_tree,
        "patient_timeline": patient.timeline,
        "patient_profile_summary": patient.profile_summary,
        "patient_psi": patient.patient_psi,

        # Interview fields
        "interview_title": interview.title,
        "interview_createdAt": interview.createdAt,
        "interview_updated_at": interview.updated_at,
        "interview_is_active": interview.is_active,
        "interview_archived": interview.archived,

        # InterviewState fields
        "state_turn_count": state.turn_count,
        "state_summary_freq": state.summary_freq,
        "state_summary_turn": state.summary_turn,
        "state_summary": state.summary,
        "state_notes": state.notes,
        "state_patient_summary": state.patient_summary,
        "state_patient_feelings": state.patient_feelings,
        "state_patient_behavior": state.patient_behavior,
    }