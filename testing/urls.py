from django.urls import path
from .views import list_mahasiswa, list_semester

app_name = 'testing'

urlpatterns = [
    path('listsemester/', list_semester, name='list_semester'),
    path('listsemester/<int:semester_id>/', list_mahasiswa, name='list_mahasiswa'),
]
