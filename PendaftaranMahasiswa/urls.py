from django.urls import path
from PendaftaranMahasiswa.views import daftar_program

app_name = 'PendaftaranMahasiswa'

urlpatterns = [
    path('', daftar_program, name='daftar_program'),  # Halaman awal
]