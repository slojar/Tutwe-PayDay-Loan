import datetime
import http.client
import time
import csv

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse

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


def download_csv(queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="loan_requests.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['EMPLOYEE ID', 'COMPANY', 'FULL NAME', 'AMOUNT REQUESTED', 'TOTAL REPAYMENT', 'DUE DATE', 'STATUS'])

    for loan_request in queryset:
        writer.writerow([
            loan_request.employee_id,
            loan_request.company.name,
            loan_request.full_name,
            loan_request.requested_amount,
            loan_request.requested_amount + loan_request.interest_amount,
            loan_request.due_date,
            loan_request.get_loan_status_display(),
        ])

    return response


def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect(reverse("home:homepage"))
    user = request.user
    status = request.GET.get('status')

    loan_requests = LoanRequest.objects.all().order_by("-created_on")
    if not user.is_staff:
        user_company_id = UserProfile.objects.get(user=user).company_id
        loan_requests = LoanRequest.objects.filter(company_id=user_company_id).order_by("-created_on")
    if status:
        loan_requests = loan_requests.filter(loan_status=status)
    total_loan = loan_requests.count()
    approved_loan = loan_requests.filter(loan_status="approved").count()
    disbursed_loan = loan_requests.filter(loan_status="disbursed").count()
    pending_loan = loan_requests.filter(loan_status="pending").count()
    decline_loan = loan_requests.filter(loan_status="declined").count()
    app_perc = 0 if total_loan == 0 or approved_loan == 0 else (approved_loan / total_loan) * 100
    dis_perc = 0 if total_loan == 0 or disbursed_loan == 0 else (disbursed_loan / total_loan) * 100 
    pen_perc = 0 if total_loan == 0 or pending_loan == 0 else (pending_loan / total_loan) * 100 
    dec_perc = 0 if total_loan == 0 or decline_loan == 0 else (decline_loan / total_loan) * 100 

    paginator = Paginator(loan_requests, 10)  # Show 10 requests per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.GET.get('download_csv'):
        return download_csv(loan_requests)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'html': render_to_string('home/loan_requests_list.html', {'loan_requests': page_obj},request=request),
            'page_number': page_number,
            'num_pages': paginator.num_pages,
        })

    context = {
        "loan_requests": page_obj,
        "tloan": total_loan,
        "aploan": approved_loan,
        "disloan": disbursed_loan,
        "ploan": pending_loan,
        "decloan": decline_loan,
        "apperc": app_perc,
        "disperc": dis_perc,
        "penperc": pen_perc,
        "decperc": dec_perc,
        "year": timezone.datetime.now().year,
        "loan_status_choices": LoanRequest.LOAN_STATUS_CHOICES,
         
    }

    return render(request, 'home/loan-dashboard.html', context)


def loan_detail_view(request, pk):
    loan = LoanRequest.objects.get(id=pk)
    context = {
        "loan_request": loan,
        "year": timezone.datetime.now().year
    }
    return render(request, 'home/loan-detail.html', context)


@require_POST
def change_loan_status(request, loan_id):
    loan_request = get_object_or_404(LoanRequest, id=loan_id)
    loan_request.loan_status = request.POST.get('loan_status')
    loan_request.save()
    return redirect(reverse('home:loan-detail', args=[loan_id]))


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


def update_loan_due_date(request):
    # This view will serve as a cron that gets all disbursed loan within and mark them as due on every 27th of the month
    if datetime.datetime.now().today().date().day == 27:
        LoanRequest.objects.filter(loan_status="disbursed").update(loan_status="due")
    return HttpResponse("Cron Ran Successfully")

