from django.urls import path

from PendaftaranMahasiswaKP import views
from PendaftaranMahasiswaKP.views import daftar_kp, kp_berhasil, daftar_kp_gagal

app_name = 'PendaftaranMahasiswaKP'

urlpatterns = [
    path("kp/", daftar_kp, name="pendaftaran_kp"),
    path("kp/kp-berhasil/<int:pendaftaran_id>/", kp_berhasil, name="kp_berhasil"),
    path('daftar/gagal/', daftar_kp_gagal, name='daftar_mbkm_gagal'),
]