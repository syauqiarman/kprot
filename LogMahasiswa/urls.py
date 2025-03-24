from django.urls import path
from . import views

app_name = 'LogMahasiswa'

urlpatterns = [
    path('buat-log/', views.buat_log, name='buat_log'),
    path('daftar-log/', views.daftar_log, name='daftar_log'),
]