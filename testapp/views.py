from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from testapp.models import *
from testapp.filters import MahasiswaFilter
from django.db.models import Q

# Create your views here.
def list_semester(request):
    semesters = Semester.objects.all().order_by('-tahun', '-gasal_genap')  # Urutkan semester terbaru dulu
    return render(request, 'list_semester.html', {'semesters': semesters})

def list_mahasiswa(request, semester_id=None):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    if semester_id: 
        semester = get_object_or_404(Semester, id=semester_id)
    else:
        semester = get_object_or_404(Semester, aktif=True)

    # Menggunakan satu query dengan Q object
    mahasiswa = Mahasiswa.objects.filter(
        Q(pendaftarankp__semester=semester) | Q(pendaftaranmbkm__semester=semester)
    ).distinct()

    # Menerapkan filter tambahan dari django-filters
    mahasiswa_filter = MahasiswaFilter(request.GET, queryset=mahasiswa)

    return render(request, 'list_mahasiswa.html', {
        'semester': semester,
        'filter': mahasiswa_filter
    })

    
