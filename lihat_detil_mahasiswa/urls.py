from django.urls import path
from .views import pendaftaran_kp_by_mahasiswa, pendaftaran_mbkm_by_mahasiswa, approve_reject_pendaftaran_mbkm

urlpatterns = [
    path('pendaftaran/kp/<int:mahasiswa_id>/', pendaftaran_kp_by_mahasiswa, name='pendaftaran_kp_by_mahasiswa'),
    path('pendaftaran/mbkm/<int:mahasiswa_id>/', pendaftaran_mbkm_by_mahasiswa, name='pendaftaran_mbkm_by_mahasiswa'),
    path('pendaftaran/kp/<int:mahasiswa_id>/<int:semester_id>/', pendaftaran_kp_by_mahasiswa, name='pendaftaran_kp_by_mahasiswa_semester'),
    path('pendaftaran/mbkm/<int:mahasiswa_id>/<int:semester_id>/', pendaftaran_mbkm_by_mahasiswa, name='pendaftaran_mbkm_by_mahasiswa_semester'),
    path('pendaftaran/mbkm/<int:pendaftaran_id>/<str:action>/', approve_reject_pendaftaran_mbkm, name='approve_reject_pendaftaran_mbkm'),
]
