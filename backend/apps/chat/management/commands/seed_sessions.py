from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.chat.models import Patient, Interviewer, Interview, InterviewState, Message

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed test interview sessions'

    def handle(self, *args, **kwargs):
        user = User.objects.first()
        if not user:
            self.stdout.write('No users found. Create a user first.')
            return

        sessions = [
            {
                'patient': {'name': 'Sarah Mitchell',  'age': 34, 'gender': 'Female',  'disorder': 'MDD', 'occupation': 'Teacher',        'ethnicity': 'White / Caucasian'},
                'title': 'Session #1 — MDD Initial',
                'messages': [
                    ('user',    'Hello, how are you feeling today?'),
                    ('patient', 'I don\'t know... just really tired all the time.'),
                    ('user',    'Can you tell me more about that?'),
                    ('patient', 'It\'s like no matter how much I sleep, nothing helps.'),
                    ('user',    'How long has this been going on?'),
                ]
            },
            {
                'patient': {'name': 'James Okafor',    'age': 27, 'gender': 'Male',    'disorder': 'GAD', 'occupation': 'Software Engineer', 'ethnicity': 'Black / African American'},
                'title': 'Session #2 — GAD Follow-up',
                'messages': [
                    ('user',    'What\'s been on your mind this week?'),
                    ('patient', 'Everything. Work deadlines, my relationship, money...'),
                    ('user',    'That sounds overwhelming. Where does the worry start?'),
                ]
            },
            {
                'patient': {'name': 'Linda Chow',      'age': 45, 'gender': 'Female',  'disorder': 'PPD', 'occupation': 'Accountant',       'ethnicity': 'East Asian'},
                'title': 'Session #3 — PPD Assessment',
                'archived': True,
                'messages': [
                    ('user',    'How have things been at work lately?'),
                    ('patient', 'People are always watching me. I can feel it.'),
                ]
            },
            {
                'patient': {'name': 'Daniel Reyes',    'age': 19, 'gender': 'Male',    'disorder': 'MDD', 'occupation': 'Student',          'ethnicity': 'Hispanic / Latino'},
                'title': 'Session #4 — MDD Student',
                'messages': []
            },
            {
                'patient': {'name': 'Priya Nair',      'age': 38, 'gender': 'Female',  'disorder': 'GAD', 'occupation': 'Nurse',            'ethnicity': 'South Asian'},
                'title': 'Session #5 — GAD Healthcare',
                'messages': [
                    ('user',    'You mentioned last time you struggle to switch off after shifts.'),
                    ('patient', 'Yes, I keep replaying everything. Did I do enough? Did I miss something?'),
                    ('user',    'That sounds like a heavy burden to carry home every day.'),
                    ('patient', 'It is. I haven\'t slept properly in weeks.'),
                ]
            },
        ]

        for s in sessions:
            p_data = s['patient']
            patient = Patient.objects.create(
                name=p_data['name'], age=p_data['age'], gender=p_data['gender'],
                disorder=p_data['disorder'], occupation=p_data['occupation'],
                ethnicity=p_data['ethnicity'], createdBy=user
            )
            # Create Interview first (no interviewer yet)
            interview = Interview.objects.create(
                createdBy=user, patient=patient,
                title=s['title'], archived=s.get('archived', False)
            )
            # Now create Interviewer linked to interview
            Interviewer.objects.create(interview=interview)

            InterviewState.objects.create(interview=interview, turn_count=len(s['messages']))
            for role, content in s['messages']:
                Message.objects.create(interview=interview, role=role, content=content)

            self.stdout.write(f'  ✓ Created: {s["title"]}')