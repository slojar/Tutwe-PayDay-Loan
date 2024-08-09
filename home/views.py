import time

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string

from home.forms import LoginForm, CompanyCreationForm, LoanRequestForm, UserAdditionForm
from home.models import LoanRequest, UserProfile, Company


def home_view(request):
    context = {
        "clients": Company.objects.all().order_by("?")[:6],
        "year": timezone.datetime.now().year
    }
    return render(request, 'home/index.html', context)


def how_it_works_view(request):
    context = {
        "year": timezone.datetime.now().year
    }
    return render(request, 'home/how-it-works.html', context)


def clients_view(request):
    context = {
        "clients": Company.objects.all().order_by("?"),
        "year": timezone.datetime.now().year
    }
    return render(request, 'home/clients.html', context)


def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect(reverse("home:homepage"))
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
        "penperc": pen_perc,
        "year": timezone.datetime.now().year
    }
    return render(request, 'home/loan-dashboard.html', context)


def loan_detail_view(request, pk):
    loan = LoanRequest.objects.get(id=pk)
    context = {
        "loan_request": loan,
        "year": timezone.datetime.now().year
    }
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
        "year": timezone.datetime.now().year
    }
    return render(request, 'home/login.html', context)


def loanrequest_view(request):
    form = LoanRequestForm()
    if request.method == 'POST':
        form = LoanRequestForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            employee_id = form.cleaned_data.get('employee_id')
            address = form.cleaned_data.get('address')
            phone = form.cleaned_data.get('phone')
            income = form.cleaned_data.get('income')
            company_id = form.cleaned_data.get('budget')
            amount_needed = form.cleaned_data.get('needed')
            purpose = form.cleaned_data.get('purpose')

            # Calculate interest
            interest_rate = 0.1  # 10%
            interest_amount = float(interest_rate) * float(amount_needed)
            # Set due date to end of the month (27th)
            due = timezone.now().today().replace(day=27)
            # Create Loan request
            LoanRequest.objects.create(
                full_name=name, email=email, employee_id=employee_id, address=address, mobile_number=phone,
                monthly_income=income, company_id=company_id, requested_amount=amount_needed, loan_purpose=purpose,
                interest_amount=interest_amount, due_date=due
            )
            messages.success(request, 'Loan Request submitted, we will reach out to you shortly!', )
            time.sleep(3)
            return redirect('/loan-request')

    company_list = [{"id": company.id, "name": company.name} for company in Company.objects.all().order_by("name")]
    context = {
        "company": company_list,
        "year": timezone.datetime.now().year
    }
    return render(request, 'home/loanform.html', context)


def contactus_view(request):
    context = {
        "year": timezone.datetime.now().year
    }
    return render(request, 'home/contact-us.html', context)


def new_client_view(request):
    form = CompanyCreationForm()
    if request.method == 'POST':
        form = CompanyCreationForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            description = form.cleaned_data.get('description')
            address = form.cleaned_data.get('address')
            logo = request.FILES['logo']
            # Create Company
            Company.objects.create(name=name, description=description, address=address, logo=logo)
            messages.success(request, 'Client/Company added successfully!')
            return redirect('/clients')

    context = {
        "year": timezone.datetime.now().year
    }
    return render(request, 'home/new-client.html', context)


def users_view(request):
    context = {
        "users": UserProfile.objects.filter(user__is_staff=False),
        "year": timezone.datetime.now().year
    }
    return render(request, 'home/company-users.html', context)


def new_user_view(request):
    form = UserAdditionForm()
    if request.method == 'POST':
        form = UserAdditionForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone')
            company_id = form.cleaned_data.get('budget')

            query = Q(username__iexact=email) | Q(email__iexact=email)

            if User.objects.filter(query).exists():
                messages.error(request, "User with this email already exist")
                return redirect('/add-user')

            password = get_random_string(length=10)

            # Create user instance
            user = User.objects.create(
                first_name=first_name, last_name=last_name, password=make_password(password), email=email,
                username=email
            )
            UserProfile.objects.create(user=user, company_id=company_id, phone_number=phone, email=email)
            messages.success(request, f'New user created with password: {password}!', )
            return redirect('/add-user')

    company_list = [{"id": company.id, "name": company.name} for company in Company.objects.all().order_by("name")]
    context = {
        "company": company_list,
        "year": timezone.datetime.now().year
    }
    return render(request, 'home/new-user.html', context)


def userlogout(request):
    logout(request)
    return redirect('/')

