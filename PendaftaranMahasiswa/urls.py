from django.urls import path
from .views import daftar_mbkm

urlpatterns = [
    path('daftar/', daftar_mbkm, name='daftar_mbkm'),
]
