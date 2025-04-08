from django.urls import path
from lihat_laporan_kegiatan.views import lihat_laporan_kegiatan, temp_dashboard_penyelia, persetujuan_laporan

app_name = 'lihat_laporan_kegiatan'

urlpatterns = [
    path('penyelia/lihat/<str:program>/<int:mahasiswa_id>/', lihat_laporan_kegiatan, name='lihat_laporan_kegiatan'),
    path('penyelia/dashboard/', temp_dashboard_penyelia, name='temp_dashboard_penyelia'),
    path('penyelia/persetujuan/<str:program>/<int:id_mahasiswa>/', persetujuan_laporan, name='persetujuan_laporan'),
]