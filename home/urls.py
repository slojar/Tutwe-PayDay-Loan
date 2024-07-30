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
    path('profile', profile_view, name='profile'),
    path('loan-request', loanrequest_view, name='loan-request'),
    path('contact-us', contactus_view, name='contact-us'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


