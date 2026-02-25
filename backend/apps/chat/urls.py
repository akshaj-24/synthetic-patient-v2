from django.urls import path
from . import views

urlpatterns = [
    path('new/',                        views.new_interview,   name='new_interview'),
    path('load/user/',                  views.load_user,       name='load_user'),
    path('load/all/',                   views.load_all,        name='load_all'),
    path('load/<int:interview_id>/',    views.load_interview,  name='load_interview'),
    path('<int:interview_id>/',         views.chat_view,       name='chat'),
    path('<int:interview_id>/send/',    views.send_message,    name='send_message'),
    path('<int:interview_id>/end/',     views.end_interview,   name='end_interview'),
    path('generate/field/',             views.generate_field,  name='generate_field'),
    path('patients/list/',              views.patient_list,    name='patient_list'),
    path('patients/<int:patient_id>/',  views.patient_detail,  name='patient_detail'),
]
