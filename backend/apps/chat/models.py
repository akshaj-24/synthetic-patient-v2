from django.db import models
from django.contrib.auth.models import User

from django.conf import settings


class NewSessionSettings(models.Model):
    """Global generation settings used on the New Session page (no interview yet)."""
    user        = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='newSessionSettings')
    model       = models.CharField(max_length=100, default='qwen3:32b')
    temperature = models.FloatField(default=1.0)   # mirrors DEFAULT_SETTINGS.GENERATION

    def __str__(self):
        return f"NewSessionSettings for {self.user.username}"


class ChatSettings(models.Model):
    """Per-interview LLM settings for both the patient and interviewer models."""
    interview                = models.OneToOneField('Interview', on_delete=models.CASCADE, related_name='chatSettings')

    # Patient model
    patient_model            = models.CharField(max_length=100, default='qwen3:32b')
    patient_temperature      = models.FloatField(default=0.7)   # mirrors DEFAULT_SETTINGS.PATIENT

    # Interviewer model
    interviewer_model        = models.CharField(max_length=100, default='qwen3:32b')
    interviewer_temperature  = models.FloatField(default=0.3)   # mirrors DEFAULT_SETTINGS.INTERVIEWER

    def __str__(self):
        return f"ChatSettings for Interview #{self.interview_id}"


class Patient(models.Model):
    name                 = models.CharField(max_length=100, blank=True)
    age                  = models.IntegerField(null=True, blank=True)
    gender               = models.CharField(max_length=20, blank=True)
    ethnicity            = models.CharField(max_length=50, blank=True)
    education            = models.CharField(max_length=200, blank=True)
    occupation           = models.CharField(max_length=200, blank=True)
    disorder             = models.TextField(blank=True)
    type                 = models.JSONField(default=list, blank=True)
    marital_status       = models.CharField(max_length=50, blank=True)

    # History (split)
    childhood_history    = models.TextField(blank=True)
    education_history    = models.TextField(blank=True)
    occupation_history   = models.TextField(blank=True)
    relationship_history = models.TextField(blank=True)
    medical_history      = models.TextField(blank=True)
    personal_history     = models.TextField(blank=True)
    session_history      = models.TextField(blank=True)

    helpless_beliefs     = models.JSONField(default=list, blank=True)
    unlovable_beliefs    = models.JSONField(default=list, blank=True)
    worthless_beliefs    = models.JSONField(default=list, blank=True)
    intermediate_belief  = models.TextField(blank=True)
    coping_strategies    = models.TextField(blank=True)
    trigger              = models.TextField(blank=True)
    auto_thoughts        = models.TextField(blank=True)
    base_emotions        = models.JSONField(default=list, blank=True)
    behavior             = models.TextField(blank=True)
    intake               = models.TextField(blank=True)
    vignette             = models.TextField(blank=True)
    family_tree          = models.TextField(blank=True)
    timeline             = models.TextField(blank=True)
    createdBy            = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='patients')
    createdAt            = models.DateTimeField(auto_now_add=True)
    profile_summary      = models.TextField(blank=True)
    patient_psi          = models.BooleanField(default=False)  # True if patient is from the Patient PSI CM dataset

    
    def __str__(self):
        return f"#{self.id} — {self.name}"

class Interviewer(models.Model):
    instructions  = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    interview    = models.OneToOneField('Interview', on_delete=models.CASCADE, related_name='interviewer')
    
    def __str__(self):
        return f"#{self.id} INTERVIEWER"


class InterviewState(models.Model):
    """Internal"""
    
    interview = models.OneToOneField('Interview', on_delete=models.CASCADE, related_name='state', default=0)
    
    turn_count    = models.IntegerField(default=0)
    summary_freq  = models.IntegerField(default=5)
    summary_turn  = models.IntegerField(default=0)
    summary       = models.TextField(blank=True)
    notes         = models.TextField(blank=True)
    patient_summary = models.TextField(blank=True)
    patient_feelings = models.TextField(blank=True)
    patient_behavior = models.TextField(blank=True)
    
    def __str__(self):
        return f"#{self.id} STATE for Interview #{self.interview.id}"

class Interview(models.Model):
    # Ownership
    createdBy    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='interviews')

    # Linked classes
    patient       = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, related_name='interviews')

    # Metadata
    title         = models.CharField(max_length=200, blank=True)
    createdAt     = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)
    is_active     = models.BooleanField(default=False)  # True when currently in chat
    archived      = models.BooleanField(default=False)

    def __str__(self):
        return f"Interview #{self.id} createdAT {self.createdAt.strftime('%Y-%m-%d %H:%M:%S')} by {self.createdBy.username if self.createdBy else 'USER DELETED'}"


class Message(models.Model):
    
    ROLE_CHOICES = [('user', 'User'), ('patient', 'Patient'), ('system', 'System')]
    interview  = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name='messages')
    role       = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content    = models.TextField()
    timestamp  = models.DateTimeField(auto_now_add=True)
    tone       = models.TextField(blank=True)  # e.g., 'neutral', 'empathetic', 'hostile and angry staring at wall'

    def __str__(self):
        return f"#{self.id} — {self.role} message in Interview #{self.interview.id} createdAT {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        ordering = ['timestamp']
