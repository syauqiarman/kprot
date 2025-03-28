from django.urls import path

from PendaftaranMahasiswa import views
from PendaftaranMahasiswa.views import daftar_kp

app_name = 'PendaftaranMahasiswa'

urlpatterns = [
    path("kp/", daftar_kp, name="pendaftaran_kp"),
    path("kp/kp-berhasil/<int:pendaftaran_id>/", views.kp_berhasil, name="kp_berhasil"),
]