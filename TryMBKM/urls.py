from django.urls import path
from .views import show_dashboard, daftar_mbkm

app_name = 'TryMBKM'

urlpatterns = [
    path('', show_dashboard, name='show_dashboard'),
    path('daftar-mbkm', daftar_mbkm, name='daftar_mbkm'),
]