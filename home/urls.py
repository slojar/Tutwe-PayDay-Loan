from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static


app_name = 'home'

urlpatterns = [
    path('', home_view, name='homepage'),
    path('how-it-works', how_it_works_view, name='how-it-works'),
    path('clients', clients_view, name='clients'),
    path('dashboard', dashboard_view, name='dashboard'),
    path('login', login_view, name='login'),
    # path('profile', profile_view, name='profile'),
    path('loan-request', loanrequest_view, name='loan-request'),
    path('contact-us', contactus_view, name='contact-us'),
    path('logout', userlogout, name='logout'),
    path('new-client', new_client_view, name='new-client'),
    path('add-user', new_user_view, name='new-user'),
    path('users', users_view, name='users'),
    path('loan-detail/<int:pk>', loan_detail_view, name='loan-detail'),
    path('loan/<int:loan_id>/change-status/', change_loan_status, name='change_loan_status'),
    path('cron', update_loan_due_date, name='cron'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


