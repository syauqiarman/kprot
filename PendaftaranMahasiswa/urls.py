from django.urls import path
from . import views

urlpatterns = [
    path('daftar/', views.daftar_mbkm, name='daftar_mbkm'),
    path('daftar/berhasil/<int:pendaftaran_id>/', views.daftar_berhasil, name='daftar_berhasil'),
]