from langfuse import get_client, observe
from langfuse.openai import OpenAI
from dotenv import load_dotenv
from . import SETTINGS as OLLAMA_SETTINGS
from . import DEFAULT_SETTINGS
from django.contrib.auth.models import User as username
from django.conf import settings
from . import schemas as MODELS
import json
from pydantic import ValidationError
import concurrent.futures
from . import tools as TOOLS
        
load_dotenv()
langfuse = get_client()

client = OpenAI(base_url=OLLAMA_SETTINGS.BASE_URL, api_key=OLLAMA_SETTINGS.API_KEY)


def call(id: str, interview, sys, user, settings = None, metadata: list = None, metadata_fields: list = None, tools:bool=False):
    
    if settings is None:
        settings = getSettings(interview, id)
    
    schema = getSchema(id)
    schema_class = getSchemaClass(id)
    
    meta_dict = dict(zip(metadata_fields, metadata)) if (metadata and metadata_fields) else {}
    
    messages=[
            {"role": "system", "content": sys},
            {"role": "user", "content": user},
        ]
    
    callArgs = {
        "model": settings["model"],
        "messages": messages,
        "temperature": settings["temperature"],
        "max_tokens": settings["max_tokens"],
        "response_format": schema,
        "langfuse_metadata": {"call_id": id, **meta_dict},
    }
    
    if tools:
        callArgs["tools"] = TOOLS.TOOL_LIST
        callArgs["tool_choice"] = "auto"
        
    for _ in range(3):
        resp = client.chat.completions.create(**callArgs)
        msg = resp.choices[0].message
        
        if not tools or not msg.tool_calls:
            break  # Exit loop if no tools or tool calls    
    
        callArgs["messages"].append(msg)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(execute_tool, tc.function.name, tc.function.arguments, interview, id): tc
                for tc in msg.tool_calls
            }
            for future, tc in futures.items():
                callArgs["messages"].append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": str(future.result()),
                })
                
    raw = msg.content
    
    if schema_class:
        try:
            return schema_class.model_validate_json(raw)  # Returns validated Pydantic object
        except ValidationError as e:
            
            langfuse.update_current_observation(
                level="WARNING",
                status_message=str(e),
                metadata={"retry": True, "call_id": id}
            )
            
            with open("llm_validation_errors.txt", "a") as f:
                f.write("ValidationError:\n")
                f.write(str(e))
                f.write("\nRaw response:\n")
                f.write(str(raw))
                f.write("\n---\n")
            
            if metadata and metadata_fields:
                   return call(id, interview, sys, user, metadata=metadata, metadata_fields=metadata_fields)
               
            return call(id, interview, sys, user)  # Retry without metadata
            
    return raw
    
# ------------------- HELPERS ----------------------
    
IDS = {
    "patient_summary": "Use for summary calls",
    "patient_content": "Use for patient response content",
    "patient_tone": "Use for patient response tone",
    "patient_behavior": "Use for patient response behavior",
    "patient_feelings": "Use for patient feelings",
    "patient_grader": "Use for verifying response for content and feelings",
    "autogenerate": "Use for autogenerating patient profile",
    "interviewer": "Use for interviewer autogen question",
    "interviewer_summary": "Use for interviewer summary",
}

def getSettings(interview, id):
    
    if id in ["patient_content", "patient_tone", "patient_behavior", "patient_grader"]:
        userSettings = interview.chatSettings
        temperature = userSettings.patient_temperature
        model = userSettings.patient_model
        
    elif id in ["autogenerate"]:
        userSettings = interview.newSessionSettings
        temperature = userSettings.temperature
        model = userSettings.model
        
    elif id in ["interviewer"]:
        userSettings = interview.chatSettings
        temperature = userSettings.interviewer_temperature
        model = userSettings.interviewer_model
        
    elif id == "interviewer_summary":
        temperature = OLLAMA_SETTINGS.INTERVIEW_SUMMARY["temperature"]
        model = interview.chatSettings.interviewer_model
        
    elif id == "patient_summary":
        temperature = OLLAMA_SETTINGS.PATIENT_SUMMARY["temperature"]
        model = interview.chatSettings.patient_model
        
    elif id == "patient_feelings":
        temperature = OLLAMA_SETTINGS.FEELINGS["temperature"]
        model = interview.chatSettings.patient_model
        
    else:
        temperature = DEFAULT_SETTINGS.GENERATION["temperature"]
        model = DEFAULT_SETTINGS.GENERATION_MODEL
        
    return {
        "temperature": temperature,
        "model": model,
        "max_tokens": DEFAULT_SETTINGS.NUM_CTX,
    }
    
def getSchema(id):
    return MODELS.getSchema(id)

def getSchemaClass(id):
    return MODELS.SCHEMA_MAP.get(id, None)

def execute_tool(tool_name, tool_args, interview, id):
    # args = json.loads(tool_args)
    patient = interview.patient
    field_map = {
            "get_childhood_history":    patient.childhood_history,
            "get_education_history":    patient.education_history,
            "get_occupation_history":   patient.occupation_history,
            "get_relationship_history": patient.relationship_history,
            "get_medical_history":      patient.medical_history,
            "get_personal_history":     patient.personal_history,
            "get_session_history":      patient.session_history,
        }
    result = field_map.get(tool_name)

    if result is None:
        langfuse.update_current_observation(
            level="WARNING",
            status_message=f"Tool not found: {tool_name}",
            metadata={"tool_name": tool_name, "call_id": id}
        )
        return "__TOOL__ERROR__"

    if not result.strip():
        langfuse.update_current_observation(
            level="WARNING",
            status_message=f"Tool returned empty: {tool_name}",
            metadata={"tool_name": tool_name, "call_id": id}
        )
        return "__TOOL__ERROR__"

    return result