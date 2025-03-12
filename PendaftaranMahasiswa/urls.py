from django.urls import path
from . import views

app_name = 'PendaftaranMahasiswa'

urlpatterns = [
    path('daftar/', views.daftar, name='daftar'),  # Halaman awal
]