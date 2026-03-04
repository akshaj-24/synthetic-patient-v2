from langfuse import get_client, observe
from langfuse.openai import OpenAI
from dotenv import load_dotenv
from . import SETTINGS as OLLAMA_SETTINGS
from . import DEFAULT_SETTINGS


load_dotenv()
langfuse = get_client()

client = OpenAI(base_url=OLLAMA_SETTINGS.BASE_URL, api_key=OLLAMA_SETTINGS.API_KEY)


def call(id, metadata, metadata_fields, sys, user, settings):
    
    
    
    resp = client.chat.completions.create(
        model=settings["model"],
        messages=[
            {"role": "system", "content": sys},
            {"role": "user", "content": user},
        ],
        temperature=settings["temperature"],
        max_tokens=settings["max_tokens"],
        #response_format= #TODO,
        
    )
    
    
    
    
    
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

def setID(id: str):
    return 1

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