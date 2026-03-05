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
    
    # Update patient feelings
    patient_feelings = f"Patient feelings for turn {state.turn_count}"  # Placeholder for actual feelings logic
    
    # Patient response workflow
    user_input = question["content"]
    user_tone = question["tone"]
    
    patient_metadata = {
        #TODO: FIll this
    }
    
    langfuse.update_current_trace(
        user_id=str(user_id),
        session_id=str(interview_id),
        tags=["patient_response", "patient"],
        metadata=patient_metadata)
    
    #Build metadata and fields list
    content_metadata = ["Test", "Test 2", "Test 3"]
    content_metadata_fields = ["field1", "field2", "field3"]
    
    sys = langfuse.get_prompt("patient_content_sys", version="latest")
    prompt_vars = {
        # TODO: fill as per prompt
    }
    sys = sys.compile(**prompt_vars)
        
    user = langfuse.get_prompt("patient_content_user", version="latest")
    prompt_vars_user = {
        # TODO: fill as per prompt
    }
    user = user.compile(**prompt_vars_user)
    
    # Get content from LLM
    resp = LLM.call(id="patient_content", 
                    interview=interview, 
                    sys=sys,
                    user=user,
                    settings=None,
                    metadata=content_metadata,
                    metadata_fields=content_metadata_fields,
                    )
    # Add or remove stuff
    
    # Get tone to convey
    tone = "neutral"  # Placeholder for actual tone logic
    # Get behavior to convey
    behavior = "N/A"  # Placeholder for actual behavior logic
    # Rewrite as patient
    
    # Change feelings if needed
    
    # add everything to JSON Response
    response = {
        "content": resp,
        "tone": tone,
        "behavior": behavior,
    }
    
    state.turn_count += 1
    state.save(update_fields=['turn_count'])
    
    return response


def checkAndUpdateSummary(interview):
    state = interview.state
    if state.turn_count >= state.summary_freq + state.summary_turn:  
        # UPDATE SUMMARY
        state.summary_turn = state.turn_count
        state.save(update_fields=['summary_turn'])
        
        updated_summary = f"Updated summary based on conversation so far: {getLastNTurnsString(interview)}"  # Placeholder for actual summary logic
        state.summary = state.summary + "\n" + updated_summary
        state.save(update_fields=['summary'])
        
        updated_patient_summary = f"Updated summary based on conversation so far: {getLastNTurnsString(interview)}"  # Placeholder for actual summary logic
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