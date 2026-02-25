from django.db import models
from django.contrib.auth.models import User

from django.conf import settings


class Patient(models.Model):
    id                  = models.AutoField(primary_key=True)
    name                = models.CharField(max_length=100)
    age                 = models.IntegerField(null=True, blank=True)
    gender              = models.CharField(max_length=20, blank=True)
    ethnicity           = models.CharField(max_length=50, blank=True)
    education           = models.CharField(max_length=200, blank=True)
    occupation          = models.CharField(max_length=200, blank=True)
    disorder            = models.TextField(blank=True)
    type                = models.JSONField(default=list, blank=True)
    history             = models.TextField(blank=True)
    helpless_beliefs    = models.JSONField(default=list, blank=True)
    unlovable_beliefs   = models.JSONField(default=list, blank=True)
    worthless_beliefs   = models.JSONField(default=list, blank=True)
    intermediate_belief = models.TextField(blank=True)
    coping_strategies   = models.TextField(blank=True)
    trigger             = models.TextField(blank=True)
    auto_thoughts       = models.TextField(blank=True)
    base_emotions       = models.JSONField(default=list, blank=True)
    behavior            = models.TextField(blank=True)
    intake              = models.TextField(blank=True)
    vignette            = models.TextField(blank=True)
    family_tree         = models.TextField(blank=True)
    timeline            = models.TextField(blank=True)
    createdBy           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='patients')
    createdAt           = models.DateTimeField(auto_now_add=True)

class Interviewer(models.Model):
    instructions  = models.TextField(blank=True)


class InterviewState(models.Model):
    """Internal"""
    
    interview = models.OneToOneField('Interview', on_delete=models.CASCADE, related_name='state')
    
    turn_count    = models.IntegerField(default=0)
    summary_freq  = models.IntegerField(default=5)
    summary_turn  = models.IntegerField(default=0)
    summary       = models.TextField(blank=True)
    notes         = models.TextField(blank=True)
    patient_summary = models.TextField(blank=True)
    patient_feelings = models.TextField(blank=True)
    patient_behavior = models.TextField(blank=True)

class Interview(models.Model):
    # Ownership
    createdBy    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='interviews')

    # Linked classes
    patient       = models.OneToOneField(Patient,       on_delete=models.SET_NULL, null=True)
    interviewer   = models.OneToOneField(Interviewer,   on_delete=models.SET_NULL, null=True)

    # Metadata
    title         = models.CharField(max_length=200, blank=True)
    createdAt    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)
    is_active     = models.BooleanField(default=False)  # True when currently in chat

    def __str__(self):
        return f"Interview #{self.id} — {self.patient.name} by {self.createdBy.username}"


class Message(models.Model):
    
    ROLE_CHOICES = [('user', 'User'), ('patient', 'Patient'), ('system', 'System')]
    interview  = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name='messages')
    role       = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content    = models.TextField()
    timestamp  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
