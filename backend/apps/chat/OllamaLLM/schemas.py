from pydantic import BaseModel, Field
from typing import Optional

# --- Define your schemas ---

class PatientContentResponse(BaseModel):
    content: str = Field(description="The patient's spoken response")

class PatientToneFeelingsBehaviorResponse(BaseModel):
    tone: str = Field(description="Tone of the patient response, e.g. anxious, flat, defensive")
    feelings: str = Field(description="Current emotional state of the patient")
    behavior: str = Field(description="Observed behavior cue, e.g. avoidance, eye contact, fidgeting, staring at wall")

class PatientGraderResponse(BaseModel):
    change: bool = Field(description="Whether the patient response needs to be changed based on content and feelings")
    feedback: Optional[str] = Field(description="Specific feedback on what needs to be changed if 'change' is True")

class PatientSummaryResponse(BaseModel):
    summary: str

class InterviewerSummaryResponse(BaseModel):
    summary: str

class AutogenerateResponse(BaseModel):
    content: str

class InterviewerQuestionResponse(BaseModel):
    question: str
    tone: str

SCHEMA_MAP = {
    "patient_content": PatientContentResponse,
    "patient_feelings_behavior": PatientToneFeelingsBehaviorResponse,
    "patient_grader": PatientGraderResponse,
    "patient_summary": PatientSummaryResponse,
    "interviewer_summary": InterviewerSummaryResponse,
    "autogenerate": AutogenerateResponse,
    "interviewer": InterviewerQuestionResponse,
}

def getSchema(id: str):
    model = SCHEMA_MAP.get(id)
    if model is None:
        return None  # No structured output for unknown IDs
    return {"type": "json_schema", "json_schema": {"name": id, "schema": model.model_json_schema(), "strict": True}}
