from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.urls import reverse

from home.forms import LoginForm


def home_view(request):
    context = {
        # 'plans': Lesson.objects.all().order_by('price')[:3],
    }
    return render(request, 'home/index.html', context)


def how_it_works_view(request):
    context = {
        # 'plans': Lesson.objects.all().order_by('price')[:3],
    }
    return render(request, 'home/how-it-works.html', context)


def clients_view(request):
    context = {
        # 'plans': Lesson.objects.all().order_by('price')[:3],
    }
    return render(request, 'home/clients.html', context)


def dashboard_view(request):
    context = {
        # 'plans': Lesson.objects.all().order_by('price')[:3],
    }
    return render(request, 'home/loan-dashboard.html', context)


def profile_view(request):
    context = {
        # 'plans': Lesson.objects.all().order_by('price')[:3],
    }
    return render(request, 'home/profile.html', context)


def login_view(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('/dashboard')
            else:
                messages.error(request, 'Login details are not correct')
                return redirect(reverse('home:login'))

    context = {
        # 'plans': Lesson.objects.all().order_by('price')[:3],
    }
    return render(request, 'home/login.html', context)


def loanrequest_view(request):
    context = {
        # 'plans': Lesson.objects.all().order_by('price')[:3],
    }
    return render(request, 'home/loanform.html', context)


def contactus_view(request):
    context = {
        # 'plans': Lesson.objects.all().order_by('price')[:3],
    }
    return render(request, 'home/contact-us.html', context)

