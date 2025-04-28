from django.urls import path
from testapp.views import list_mahasiswa, list_semester

app_name = 'testapp'

urlpatterns = [
    path('listsemester/', list_semester, name='list_semester'),
    path('listmahasiswa/', list_mahasiswa, name='list_mahasiswa_no_id'),
    path('listsemester/<int:semester_id>/', list_mahasiswa, name='list_mahasiswa'),
]