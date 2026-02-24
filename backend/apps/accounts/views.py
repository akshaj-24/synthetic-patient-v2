from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, LoginForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

def signup_view(request):
    form = SignupForm()
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    return render(request, 'accounts/signup.html', {'form': form})

# AJAX endpoint — checks if username exists in DB live
def check_username(request):
    username = request.GET.get('username', '')
    exists = User.objects.filter(username__iexact=username).exists()
    return JsonResponse({'exists': exists})

def login_view(request):
    form = LoginForm()
    error = ''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('home')
            error = 'Invalid username or password.'
    return render(request, 'accounts/login.html', {'form': form, 'error': error})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')   # blocks unauthenticated users
def home_view(request):
    return render(request, 'home.html')

def check_password(request):
    password = request.GET.get('password', '')
    username = request.GET.get('username', '')  # needed for similarity check

    # build a temp user object so Django can check similarity
    temp_user = User(username=username)
    try:
        validate_password(password, user=temp_user)
        return JsonResponse({'errors': []})
    except ValidationError as e:
        return JsonResponse({'errors': e.messages})