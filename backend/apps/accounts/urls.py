from django.urls import path
from . import views

urlpatterns = [
    path('signup/',                   views.signup_view,    name='signup'),
    path('login/',                    views.login_view,     name='login'),
    path('logout/',                   views.logout_view,    name='logout'),
    path('',                          views.home_view,      name='home'),
    path('check-username/',           views.check_username, name='check_username'),
    path('check-password/', views.check_password, name='check_password'),
]

