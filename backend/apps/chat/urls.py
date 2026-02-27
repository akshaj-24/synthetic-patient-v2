from django.urls import path
from . import views

urlpatterns = [
    # Session CRUD
    path('new/',                             views.new_interview,            name='new_interview'),
    path('list/',                            views.load_list,                name='load_list'),
    path('list/api/',                        views.interview_list_api,       name='interview_list_api'),
    path('load/<int:interview_id>/',         views.load_interview,           name='load_interview'),

    # Chat
    path('<int:interview_id>/',              views.chat_view,                name='chat'),
    path('<int:interview_id>/send/',         views.send_message,             name='send_message'),
    path('<int:interview_id>/end/',          views.end_interview,            name='end_interview'),
    path('<int:interview_id>/preview/',      views.interview_messages_preview, name='interview_preview'),
    path('<int:interview_id>/archive/',      views.archive_interview,        name='archive_interview'),
    path('<int:interview_id>/delete/',       views.delete_interview,         name='delete_interview'),

    # Generation
    path('generate/field/',                  views.generate_field,           name='generate_field'),

    # Patients
    path('patients/list/',                   views.patient_list,             name='patient_list'),
    path('patients/<int:patient_id>/',       views.patient_detail,           name='patient_detail'),
]
