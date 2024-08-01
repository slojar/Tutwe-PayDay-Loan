from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse

from home.forms import LoginForm
from home.models import LoanRequest, UserProfile


def home_view(request):
    context = {
    }
    return render(request, 'home/index.html', context)


def how_it_works_view(request):
    context = {
    }
    return render(request, 'home/how-it-works.html', context)


def clients_view(request):
    context = {
    }
    return render(request, 'home/clients.html', context)


def dashboard_view(request):
    user = request.user
    loan_requests = LoanRequest.objects.all().order_by("-created_on")
    if not user.is_staff:
        user_company_id = UserProfile.objects.get(user=user).company_id
        loan_requests = LoanRequest.objects.filter(company_id=user_company_id).order_by("-created_on")

    total_loan = loan_requests.count()
    approved_loan = loan_requests.filter(loan_status="approved").count()
    disbursed_loan = loan_requests.filter(loan_status="disbursed").count()
    pending_loan = loan_requests.filter(loan_status="pending").count()

    app_perc = (approved_loan / total_loan) * 100
    dis_perc = (disbursed_loan / total_loan) * 100
    pen_perc = (pending_loan / total_loan) * 100

    context = {
        "loan_requests": loan_requests,
        "tloan": total_loan,
        "aploan": approved_loan,
        "disloan": disbursed_loan,
        "ploan": pending_loan,
        "apperc": app_perc,
        "disperc": dis_perc,
        "penperc": pen_perc
    }
    return render(request, 'home/loan-dashboard.html', context)


def loan_detail_view(request, pk):
    loan = LoanRequest.objects.get(id=pk)
    context = {"loan_request": loan}
    return render(request, 'home/loan-detail.html', context)


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
    }
    return render(request, 'home/login.html', context)


def loanrequest_view(request):
    context = {
    }
    return render(request, 'home/loanform.html', context)


def contactus_view(request):
    context = {
    }
    return render(request, 'home/contact-us.html', context)


def userlogout(request):
    logout(request)
    return redirect('/')

