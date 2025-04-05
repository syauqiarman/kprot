from django.urls import path
from lihat_laporan_kegiatan.views import lihat_laporan_kegiatan

app_name = 'lihat_laporan_kegiatan'

urlpatterns = [
    path('lihat_laporan/', lihat_laporan_kegiatan, name='lihat_laporan_kegiatan'),
    # path('persetujuan_laporan/', persetujuan_laporan, name='persetujuan_laporan'),
]