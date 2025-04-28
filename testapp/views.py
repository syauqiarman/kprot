from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from testapp.models import *
from testapp.filters import MahasiswaFilter
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test

# Create your views here.
def is_dosen(user):
    return Dosen.objects.filter(user=user).exists()

def is_pa(user):
    return PembimbingAkademik.objects.filter(user=user).exists()

def is_manajemen(user):
    return Manajemen.objects.filter(user=user).exists()

@user_passes_test(lambda user: is_dosen(user) or is_pa(user) or is_manajemen(user), login_url='/login/')
def list_semester(request):
    semesters = Semester.objects.all().order_by('-tahun', '-gasal_genap')  # Urutkan semester terbaru dulu
    return render(request, 'list_semester.html', {'semesters': semesters})

@user_passes_test(lambda user: is_dosen(user) or is_pa(user) or is_manajemen(user), login_url='/login/')
def list_mahasiswa(request, semester_id=None):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    user = request.user

    if semester_id: 
        semester = get_object_or_404(Semester, id=semester_id)
    else:
        semester = get_object_or_404(Semester, aktif=True)

    mahasiswa = Mahasiswa.objects.filter(
        Q(pendaftarankp__semester=semester) | Q(pendaftaranmbkm__semester=semester)
    ).distinct()

    # Filter based on PA
    pa_instance = PembimbingAkademik.objects.filter(user=user).first()
    if is_pa(user) and pa_instance:
        mahasiswa = mahasiswa.filter(pa=pa_instance)

    # Aplikasikan filter dengan request agar filter dapat mengakses data request
    mahasiswa_filter = MahasiswaFilter(request.GET, queryset=mahasiswa, request=request)
    
    # Preprocess setelah filter untuk memastikan atribut tersedia di hasil filter
    filtered_mahasiswa = mahasiswa_filter.qs
    for mhs in filtered_mahasiswa:
        mhs.kp_instance = mhs.pendaftarankp_set.filter(semester=semester).first()
        mhs.mbkm_instance = mhs.pendaftaranmbkm_set.filter(semester=semester).first()

    return render(request, 'list_mahasiswa.html', {
        'semester': semester,
        'filter': mahasiswa_filter,
        'mahasiswa': filtered_mahasiswa,
    })


