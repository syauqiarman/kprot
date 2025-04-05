from django.urls import path
from . import views

app_name = 'LogMahasiswa'

urlpatterns = [
    path('', views.daftar_log, name='daftar_log'),
    path('buat/', views.buat_log, name='buat_log'),
    path('<int:log_id>/', views.detail_log, name='detail_log'),
    path('<int:log_id>/edit/', views.edit_log, name='edit_log'),
    path('<int:log_id>/hapus/', views.hapus_log, name='hapus_log'),
]