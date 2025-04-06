from django.urls import path
from LogMahasiswa.views import create_log, log_detail

app_name = 'LogMahasiswa'

urlpatterns = [
    path('buat/', create_log, name='create_log'),
    path('', log_detail, name='log_detail'),
]