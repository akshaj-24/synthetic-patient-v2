from ...models import Interview, Patient, Message, ChatSettings, InterviewState as State
from langfuse import observe, get_client
langfuse = get_client()
# Prompt imports



# LLM response import
from .. import LLM_CALL as LLM

@observe()
def response(interview_id, question, user_id=None):
    
    interview = Interview.objects.get(id=interview_id)
    patient = interview.patient
    state = interview.state
    chatSettings = interview.chatSettings
    
    checkAndUpdateSummary(interview)
    
    call_args = getArgs(interview, patient, state)
    
    sys = langfuse.get_prompt("response/sys/feelings", label="production")
    sys = sys.compile(**call_args)
    user = langfuse.get_prompt("response/user/feelings", label="production")
    user = user.compile(**call_args)
    
    feelings_behavior_resp = LLM.call(
        id="patient_feelings_behavior", 
        interview=interview,
        sys=sys,
        user=user,
        settings=None,
        metadata=None,
        metadata_fields=None,
        tools=True,)
    
    state.patient_feelings = feelings_behavior_resp.feelings
    state.patient_behavior = feelings_behavior_resp.behavior
    state.save(update_fields=['patient_feelings', 'patient_behavior'])
    
    # Patient response workflow
    user_input = question["content"]
    user_tone = question["tone"]
    
    all_vars = {
        **sysArgs(interview),           # all patient + state fields
        "interviewer_question": user_input,
        "interviewer_tone":     user_tone,
    }
    
    updateMetadata(user_id, interview_id, all_vars)

    # TODO Reduce number of LLM calls
    
    # TODO Build prompts in langfuse

    # TODO Refactor LLM calls

    # Get feelings and immediate beheavior based on interviewers question and tone
    sys, user = compilePrompt("patient_feelings_behavior", all_vars)
    pf_resp = LLM.call(id="patient_feelings_behavior",
                        interview=interview, 
                        sys=sys,
                        user=user,
                        settings=None,
                        metadata=None,
                        metadata_fields=None,
                        tools=True,
                    )
    
    # state.patient_feelings = pf_resp.feelings
    # state.save(update_fields=['patient_feelings'])
    
    # all_vars["patient_feelings"] = pf_resp.feelings
    
    # # Get resp content 
    # sys, user = compilePrompt("patient_content", all_vars)
    # pc_resp = LLM.call(id="patient_content", 
    #                 interview=interview, 
    #                 sys=sys,
    #                 user=user,
    #                 settings=None,
    #                 metadata=None,
    #                 metadata_fields=None,
    #                 tools=True,
    #                 )
    
    # all_vars["resp_content"] = pc_resp.content
    
    
    # # Get patients tone to response with
    # sys, user = compilePrompt("patient_tone", all_vars)
    # tone_resp = LLM.call(id="patient_tone", 
    #                 interview=interview, 
    #                 sys=sys,
    #                 user=user,
    #                 settings=None,
    #                 metadata=None,
    #                 metadata_fields=None,
    #                 tools=True,
    #                 )
    
    # all_vars["resp_tone"] = tone_resp.tone
    # tone = tone_resp.tone
    
    
    # # Get patient behavior to response with
    # sys, user = compilePrompt("patient_behavior", all_vars)
    # behavior_resp = LLM.call(id="patient_behavior",
    #                 interview=interview, 
    #                 sys=sys,
    #                 user=user,
    #                 settings=None,
    #                 metadata=None,
    #                 metadata_fields=None,
    #                 tools=True,
    #                 )
    
    # behavior = behavior_resp.behavior
    # all_vars["resp_behavior"] = behavior_resp.behavior
    
    # # Rewrite response as patient, incorporating content, tone, behavior, and feelings
    # sys, user = compilePrompt("patient_writer", all_vars)
    # resp_final = LLM.call(id="patient_writer",
    #                 interview=interview, 
    #                 sys=sys,
    #                 user=user,
    #                 settings=None,
    #                 metadata=None,
    #                 metadata_fields=None,
    #                 tools=True,
    #                 )
    
    # all_vars["resp_final"] = resp_final.content
    
    # # Judge and change if needed, or pass through if good
    # sys, user = compilePrompt("patient_grader", all_vars)
    # grader_resp = LLM.call(id="patient_grader",
    #                 interview=interview, 
    #                 sys=sys,
    #                 user=user,
    #                 settings=None,
    #                 metadata=None,
    #                 metadata_fields=None,
    #                 tools=True,
    #                 )
    
    # all_vars["resp_grader"] = grader_resp.content
    # resp = grader_resp.content
    
    # response = {
    #     "content": resp,
    #     "tone": tone,
    #     "behavior": behavior,
    #     "id": None,
    # }
    
    resp = "Test reply"
    tone = "Neutral"
    behavior = "Test"
    
    response = {
        "content": "Test Reply",
        "tone": "Neutral",
        "behavior": "Test",
        "id": None,
    }
    
    # Persist user message (store tone so it appears in transcripts)
    interview.messages.create(role='user', content=user_input, tone=tone)

    # Persist patient reply
    patient_msg = interview.messages.create(role='patient', content=resp, tone=tone, behavior=behavior)
    
    state.turn_count += 1
    state.save(update_fields=['turn_count'])
    
    langfuse.update_current_trace(
        metadata={
            "response_tone":     tone,
            "response_behavior": behavior,
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
        
        #TODO add llm calls
        updated_summary = f"Updated summary based on conversation so far: {getLastNTurnsString(interview, state.summary_freq)}"  # Placeholder for actual summary logic
        state.summary = state.summary + "\n" + updated_summary
        state.save(update_fields=['summary'])
        
        #TODO add llm calls
        updated_patient_summary = f"Updated summary based on conversation so far: {getLastNTurnsString(interview, state.summary_freq)}"  # Placeholder for actual summary logic
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
    
def updateSysUserPrompt(prompt_id, version, sys_vars=None, user_vars=None):
    sys = langfuse.get_prompt(prompt_id + "_sys", version=version)
    user = langfuse.get_prompt(prompt_id + "_user", version=version)
    sys = sys.compile(**sys_vars)
    user = user.compile(**user_vars)
    return sys, user



def sysArgs(interview):
    patient = interview.patient
    state = interview.state
    return {
        "patient_name":          patient.name,
        "patient_age":           patient.age,
        "patient_gender":        patient.gender,
        "patient_disorder":      patient.disorder,
        "patient_type":          patient.type,
        "coping_strategies":     patient.coping_strategies,
        "trigger":               patient.trigger,
        "auto_thoughts":         patient.auto_thoughts,
        "base_emotions":         patient.base_emotions,
        "intermediate_belief":   patient.intermediate_belief,
        "helpless_beliefs":      patient.helpless_beliefs,
        "unlovable_beliefs":     patient.unlovable_beliefs,
        "worthless_beliefs":     patient.worthless_beliefs,
        "behavior":              patient.behavior,
        "turn_count":            state.turn_count,
        "summary":               state.summary,
        "patient_summary":       state.patient_summary,
        "patient_feelings":      state.patient_feelings,
        "patient_behavior":      state.patient_behavior,
    }


def getSysArgs(id, version, interview):
    prompt = langfuse.get_prompt(id + "_sys", version=version)
    filtered = {k: v for k, v in sysArgs(interview).items() if k in prompt.variables}
    return filtered

def compilePrompt(prompt_id, all_vars, version="latest"):
    """Compile both sys and user prompts, filtering to only used variables."""
    sys_prompt  = langfuse.get_prompt(prompt_id + "_sys",  version=version)
    user_prompt = langfuse.get_prompt(prompt_id + "_user", version=version)

    sys  = sys_prompt.compile( **{k: v for k, v in all_vars.items() if k in sys_prompt.variables})
    user = user_prompt.compile(**{k: v for k, v in all_vars.items() if k in user_prompt.variables})
    return sys, user

def updateMetadata(user_id, interview_id, all_vars):
    langfuse.update_current_trace(
        user_id=str(user_id),
        session_id=str(interview_id),
        tags=["patient_response", "patient"],
        metadata=all_vars
    )
    
    return 1

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