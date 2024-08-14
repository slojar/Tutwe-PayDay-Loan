from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class LoanRequestForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    employee_id = forms.CharField()
    phone = forms.CharField()
    address = forms.CharField()
    income = forms.FloatField()
    budget = forms.IntegerField()
    needed = forms.FloatField()
    purpose = forms.CharField()


class UserAdditionForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    phone = forms.CharField()
    budget = forms.IntegerField()


class CompanyCreationForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField(required=False)
    address = forms.CharField(required=False)







