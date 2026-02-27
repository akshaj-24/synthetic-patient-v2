# apps/chat/admin.py
from django.contrib import admin
from .models import Patient, Interviewer, Interview, InterviewState, Message

@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display  = ('id', 'title', 'createdBy', 'patient', 'is_active', 'archived', 'createdAt')
    list_filter   = ('is_active', 'archived')
    search_fields = ('title', 'createdBy__username', 'patient__name')
    actions       = ['archive_sessions', 'unarchive_sessions']

    @admin.action(description='Archive selected sessions')
    def archive_sessions(self, request, queryset):
        queryset.update(archived=True)

    @admin.action(description='Unarchive selected sessions')
    def unarchive_sessions(self, request, queryset):
        queryset.update(archived=False)

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display  = ('id', 'name', 'age', 'gender', 'disorder', 'occupation', 'createdBy', 'createdAt')
    list_filter   = ('gender', 'disorder')
    search_fields = ('name', 'disorder', 'occupation')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display  = ('id', 'interview', 'role', 'timestamp')
    list_filter   = ('role',)
    search_fields = ('content', 'interview__title')

@admin.register(InterviewState)
class InterviewStateAdmin(admin.ModelAdmin):
    list_display  = ('id', 'interview', 'turn_count', 'summary_freq')

@admin.register(Interviewer)
class InterviewerAdmin(admin.ModelAdmin):
    list_display  = ('id', 'interview')
