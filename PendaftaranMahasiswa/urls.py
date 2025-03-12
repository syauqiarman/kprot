from django.urls import path
from . import views

app_name = 'PendaftaranMahasiswa'

urlpatterns = [
    path('', views.home, name='home'),  # Halaman awal
]