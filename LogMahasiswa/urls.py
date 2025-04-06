from django.urls import path
from . import views

urlpatterns = [
    path('buat/', views.create_log, name='create-log'),
    path('<int:log_id>/', views.log_detail, name='log-detail'),
]