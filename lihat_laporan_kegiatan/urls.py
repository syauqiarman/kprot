from django.urls import path
from lihat_laporan_kegiatan.views import lihat_laporan_kegiatan, dashboard_penyelia_sementara

app_name = 'lihat_laporan_kegiatan'

urlpatterns = [
    path('penyelia/lihat/<str:program>/<int:mahasiswa_id>/', lihat_laporan_kegiatan, name='lihat_laporan_kegiatan'),
    path('penyelia/dashboard/', dashboard_penyelia_sementara, name='dashboard_penyelia_sementara'),
    # path('persetujuan_laporan/', persetujuan_laporan, name='persetujuan_laporan'),
]