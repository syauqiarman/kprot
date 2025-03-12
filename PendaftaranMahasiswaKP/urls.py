from django.urls import path

from PendaftaranMahasiswaKP import views
from PendaftaranMahasiswaKP.views import daftar_kp

app_name = 'PendaftaranMahasiswaKP'

urlpatterns = [
    path("kp/", daftar_kp, name="pendaftaran_kp"),
    path("kp/kp-berhasil/<int:pendaftaran_id>/", views.kp_berhasil, name="kp_berhasil"),
]