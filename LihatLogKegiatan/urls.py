from django.urls import path
from .views import mahasiswa_logs, mahasiswa_list, lihat_log_mahasiswa

app_name = 'LihatLogKegiatan'

urlpatterns = [
    path('lihat-log/', mahasiswa_list, name='mahasiswa_list'),
    path('<int:mahasiswa_id>/', mahasiswa_logs, name='mahasiswa_logs'),
    path('lihat-log-mahasiswa/<int:semester_id>/', lihat_log_mahasiswa, name='lihat_log_mahasiswa'),
]