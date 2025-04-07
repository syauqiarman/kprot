from django.urls import path
from lihat_laporan_kegiatan.views import lihat_laporan_kegiatan, dashboard_penyelia_sementara, persetujuan_laporan

app_name = 'lihat_laporan_kegiatan'

urlpatterns = [
    path('penyelia/lihat/<str:program>/<int:mahasiswa_id>/', lihat_laporan_kegiatan, name='lihat_laporan_kegiatan'),
    path('penyelia/dashboard/', dashboard_penyelia_sementara, name='dashboard_penyelia_sementara'),
    path('penyelia/persetujuan/<str:program>/<int:id_mahasiswa>/', persetujuan_laporan, name='persetujuan_laporan'),
]