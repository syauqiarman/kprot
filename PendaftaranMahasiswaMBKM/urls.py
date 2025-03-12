from django.urls import path
from PendaftaranMahasiswaMBKM.views import daftar_mbkm, daftar_berhasil, daftar_mbkm_gagal

app_name = 'PendaftaranMahasiswaMBKM'

urlpatterns = [
    path('daftar/', daftar_mbkm, name='daftar_mbkm'),
    path('daftar/berhasil/<int:pendaftaran_id>/', daftar_berhasil, name='daftar_berhasil'),
    path('daftar/gagal/', daftar_mbkm_gagal, name='daftar_mbkm_gagal'),
]