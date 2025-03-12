from django.urls import path

from .views import dashboard_view, get_app_endpoints

app_name = 'dashboard'

urlpatterns = [
    path('', dashboard_view, name='home'),
]