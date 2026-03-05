from pydantic import BaseModel, Field
from typing import Optional

# --- Define your schemas ---

class PatientContentResponse(BaseModel):
    content: str = Field(description="The patient's spoken response")

class PatientToneResponse(BaseModel):
    tone: str = Field(description="Tone of the patient response, e.g. anxious, flat, defensive")

class PatientBehaviorResponse(BaseModel):
    behavior: str = Field(description="Observed behavior cue, e.g. avoidance, eye contact")

class PatientFeelingsResponse(BaseModel):
    feelings: str = Field(description="Current emotional state of the patient")
    intensity: int = Field(description="Intensity from 1-10")

class PatientGraderResponse(BaseModel):
    content_valid: bool
    feelings_valid: bool
    feedback: Optional[str] = None

class PatientSummaryResponse(BaseModel):
    summary: str

class InterviewerSummaryResponse(BaseModel):
    summary: str

class AutogenerateResponse(BaseModel):
    name: str
    age: int
    background: str
    presenting_problem: str
    personality_traits: list[str]

class InterviewerQuestionResponse(BaseModel):
    question: str
    rationale: Optional[str] = None

SCHEMA_MAP = {
    "patient_content": PatientContentResponse,
    "patient_tone": PatientToneResponse,
    "patient_behavior": PatientBehaviorResponse,
    "patient_feelings": PatientFeelingsResponse,
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
