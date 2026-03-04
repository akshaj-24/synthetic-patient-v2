from ...models import Interview, Patient, Message, ChatSettings, InterviewState as State

# Prompt imports



# LLM response import
from .. import LLM_CALL as LLM

def response(interview_id, question):
    
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
    
    
    # Get content from LLM
    resp = f"test response for '{user_input}' with tone '{user_tone}'"
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