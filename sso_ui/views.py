from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import login
from rest_framework_simplejwt.tokens import RefreshToken
from .cas_client import validate_cas_ticket
from database.models import Mahasiswa
from django.contrib.auth import logout

def cas_login(request):
    cas_login_url = f"{settings.CAS_CONFIG['CAS_URL']}/login?service={settings.CAS_CONFIG['SERVICE_URL']}"
    return redirect(cas_login_url)

def cas_callback(request):
    ticket = request.GET.get('ticket')
    if not ticket:
        return redirect('login')
    
    cas_data = validate_cas_ticket(ticket)
    if not cas_data:
        return redirect('login')
    
    # Get or create user
    user, created = Mahasiswa.objects.get_or_create(
        username=cas_data['username'],
        defaults={'email': cas_data['attributes'].get('mail', '')}
    )
    
    if created or not user.is_active:
        user.update_from_cas(cas_data)
    
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    response = redirect('dashboard')
    response.set_cookie('access_token', str(refresh.access_token), httponly=True)
    response.set_cookie('refresh_token', str(refresh), httponly=True)
    
    return response

def logout_view(request):
    logout(request)
    response = redirect('login')
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response