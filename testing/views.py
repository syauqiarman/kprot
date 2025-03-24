from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from database.models import *
from testing.filters import MahasiswaFilter
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test

# Create your views here.
def is_dosen(user):
    return Dosen.objects.filter(user=user).exists()

def is_pa(user):
    return PembimbingAkademik.objects.filter(user=user).exists()

def is_kaprodi(user):
    return Kaprodi.objects.filter(user=user).exists()

def list_semester(request):
    semesters = Semester.objects.all().order_by('-tahun', '-gasal_genap')
    return render(request, 'list_semester.html', {'semesters': semesters,
                                                  'dashboard_url': "/listmahasiswa/listsemester/",
                                                  "pendaftaran_url": "/listmahasiswa/listsemester/"})

def list_mahasiswa(request, semester_id=None):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    user = request.user

    if semester_id: 
        semester = get_object_or_404(Semester, id=semester_id)
    else:
        semester = get_object_or_404(Semester, aktif=True)

    # Menggunakan satu query dengan Q object
    mahasiswa = Mahasiswa.objects.filter(
        Q(pendaftarankp__semester=semester) | Q(pendaftaranmbkm__semester=semester)
    ).distinct()
    print(mahasiswa)

    # Ambil PA yang sesuai dengan user
    pa_instance = PembimbingAkademik.objects.filter(user=user).first()

    # Jika user adalah PA dan ada PA terkait, filter berdasarkan PA
    if is_pa(user) and not (is_dosen(user) or is_kaprodi(user)) and pa_instance:
        mahasiswa = mahasiswa.filter(pa=pa_instance)
    elif is_pa(user) and pa_instance:
        mahasiswa = mahasiswa.filter(
            Q(pa=pa_instance) | Q(pendaftarankp__semester=semester) | Q(pendaftaranmbkm__semester=semester)
        ).distinct()

    # Menerapkan filter tambahan dari django-filters
    mahasiswa_filter = MahasiswaFilter(request.GET, queryset=mahasiswa)

    return render(request, 'list_mahasiswa.html', {
        'semester': semester,
        'filter': mahasiswa_filter,
        'dashboard_url': "/listmahasiswa/listsemester/",
        "pendaftaran_url": "/listmahasiswa/listsemester/"
    })
    
