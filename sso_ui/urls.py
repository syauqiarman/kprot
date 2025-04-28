from django.urls import path
from sso_ui.views import cas_login, cas_callback

urlpatterns = [
    path('login/', cas_login, name='login'),
    path('cas/callback/', cas_callback, name='cas_callback'),
]