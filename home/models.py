from django.contrib.auth.models import User
from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=250, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    logo = models.ImageField(upload_to="company-images", blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    update_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = "company"
        verbose_name_plural = "companies"


class LoanRequest(models.Model):
    LOAN_STATUS_CHOICES = (
        ("pending", "Awaiting Approval"), ("approved", "Approved"), ("disbursed", "Disbursed"),
        ("declined", "Declined"),
        ("due", "Due For Repayment"), ("repaid", "Repayment Complete")
    )

    full_name = models.CharField(max_length=300)
    email = models.EmailField(blank=True, null=True)
    employee_id = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    monthly_income = models.FloatField(default=0)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, blank=True, null=True)
    requested_amount = models.FloatField(blank=True, null=True, max_length=20)
    interest_amount = models.FloatField(blank=True, null=True, max_length=20)
    date_disbursed = models.DateTimeField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    loan_purpose = models.TextField(blank=True, null=True)
    loan_status = models.CharField(choices=LOAN_STATUS_CHOICES, max_length=20, default="pending")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} - Amount: {self.requested_amount}"

    class Meta:
        db_table = "loanrequest"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(max_length=200)

    def __str__(self):
        return f"{self.user.username}: {self.company.name}"

    class Meta:
        db_table = "profile"
