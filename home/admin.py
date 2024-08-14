from django.contrib import admin

from home.models import Company, LoanRequest, UserProfile

admin.site.register(Company)
admin.site.register(LoanRequest)
admin.site.register(UserProfile)

