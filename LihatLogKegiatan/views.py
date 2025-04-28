from django.shortcuts import get_object_or_404, render, redirect
from testapp.models import *
from django.db.models import Q, Sum, Prefetch
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

def is_penyelia(user):
    return Penyelia.objects.filter(user=user).exists()

def is_dosen(user):
    return Dosen.objects.filter(user=user).exists()

def is_mahasiswa(user):
    return Mahasiswa.objects.filter(user=user).exists()

# @login_required
def mahasiswa_list(request):
    # if not (is_dosen(request.user) or is_penyelia(request.user)):
    #     return render(request, 'gagal_lihat_log.html', status=403)
    
    if is_dosen(request.user):
        mahasiswas = Mahasiswa.objects.all().select_related('user')
    else:  # Penyelia
        penyelia_obj = Penyelia.objects.get(user=request.user) 
        mahasiswas = Mahasiswa.objects.filter(
            Q(pendaftarankp__penyelia=penyelia_obj) |
            Q(pendaftaranmbkm__penyelia=penyelia_obj)
        ).distinct().select_related('user')
    
    # Annotate each mahasiswa with their program type and total hours
    mahasiswa_data = []
    for mahasiswa in mahasiswas:
        # Get program registrations
        kp_registrations = PendaftaranKP.objects.filter(mahasiswa=mahasiswa)
        mbkm_registrations = PendaftaranMBKM.objects.filter(mahasiswa=mahasiswa)
        
        # Determine program types
        program_type = []
        if kp_registrations.exists():
            program_type.append("KP")
        if mbkm_registrations.exists():
            program_type.append("MBKM")
        
        # Calculate total approved hours more efficiently
        kp_hours = LogMingguan.objects.filter(
            pendaftaran_kp__in=kp_registrations,
            status_persetujuan='disetujui'
        ).aggregate(total=Sum('total_jam'))['total'] or 0.0
        
        mbkm_hours = LogMingguan.objects.filter(
            pendaftaran_mbkm__in=mbkm_registrations,
            status_persetujuan='disetujui'
        ).aggregate(total=Sum('total_jam'))['total'] or 0.0
        
        total_hours = kp_hours + mbkm_hours
        
        mahasiswa_data.append({
            'mahasiswa': mahasiswa,
            'program_type': ", ".join(program_type) if program_type else "-",
            'total_hours': total_hours
        })
    
    context = {
        'mahasiswa_data': mahasiswa_data, 
        'empty_message': 'No mahasiswa found'
    }
    return render(request, 'list_mahasiswa_ke_log.html', context)

# @user_passes_test(lambda user: is_dosen(user) or is_penyelia(user) or is_mahasiswa(user), login_url='/temp_login/')
def mahasiswa_logs(request, mahasiswa_id):
    mahasiswa = get_object_or_404(Mahasiswa, id=mahasiswa_id)
    
    if is_mahasiswa(request.user) and request.user.mahasiswa.id != mahasiswa.id:
        return HttpResponseForbidden("Anda hanya dapat melihat data diri sendiri.")
    
    elif is_penyelia(request.user):
        is_supervised = (
            PendaftaranKP.objects.filter(mahasiswa=mahasiswa, penyelia=request.user.penyelia).exists() or
            PendaftaranMBKM.objects.filter(mahasiswa=mahasiswa, penyelia=request.user.penyelia).exists()
        )
        if not is_supervised:
            return HttpResponseForbidden("Anda hanya dapat melihat mahasiswa bimbingan Anda.")
    
    registration = (
        PendaftaranKP.objects.filter(mahasiswa=mahasiswa).first() or
        PendaftaranMBKM.objects.filter(mahasiswa=mahasiswa).first()
    )
    
    logs = None
    if registration:
        if isinstance(registration, PendaftaranKP):
            logs = LogMingguan.objects.filter(pendaftaran_kp=registration)
        elif isinstance(registration, PendaftaranMBKM):
            logs = LogMingguan.objects.filter(pendaftaran_mbkm=registration)
            
        if logs is not None:
            logs = logs.prefetch_related(
                Prefetch('aktivitas_harian', queryset=AktivitasHarian.objects.order_by('tanggal'))
            ).order_by('-tanggal_mulai')
    
    context = {
        'mahasiswa': mahasiswa,
        'registration': registration,
        'logs': logs,
        'is_dosen': is_dosen(request.user),
        'is_penyelia': is_penyelia(request.user),
        'empty_message': "Mahasiswa belum memiliki catatan log mingguan.",
    }
    
    return render(request, 'list_log_mahasiswa.html', context)


def lihat_log_mahasiswa(request, semester_id=None):
    
    user = request.user

    if semester_id: 
        semester = get_object_or_404(Semester, id=semester_id)
    else:
        semester = get_object_or_404(Semester, aktif=True)

    # Menggunakan satu query dengan Q object
    mahasiswa = Mahasiswa.objects.filter(
        Q(pendaftarankp__semester=semester) | Q(pendaftaranmbkm__semester=semester)
    ).distinct()

    hasil = []

    for mhs in mahasiswa:
        # Cek apakah dia daftar KP / MBKM semester ini
        pendaftaran_kp = mhs.pendaftarankp_set.filter(semester=semester).first()
        pendaftaran_mbkm = mhs.pendaftaranmbkm_set.filter(semester=semester).first()

        log = None
        program = None
        tanggal_mulai = None
        tanggal_selesai = None

        log = LogMingguan.objects.filter(
        Q(pendaftaran_kp__mahasiswa=mhs, pendaftaran_kp__semester=semester) |
        Q(pendaftaran_mbkm__mahasiswa=mhs, pendaftaran_mbkm__semester=semester)
        ).first()

        if log and log.pendaftaran_kp and log.pendaftaran_kp.semester == semester:
            program = "KP"
            tanggal_mulai = log.pendaftaran_kp.tanggal_mulai
            tanggal_selesai = log.pendaftaran_kp.tanggal_selesai
        elif log and log.pendaftaran_mbkm and log.pendaftaran_mbkm.semester == semester:
            program = "MBKM"
            tanggal_mulai = log.pendaftaran_mbkm.tanggal_mulai
            tanggal_selesai = log.pendaftaran_mbkm.tanggal_selesai
        else:
            tanggal_mulai = None
            tanggal_selesai = None

        if log:
            total_jam = 0
            status_log = log.status_persetujuan  # ambil dari field di model
        else:
            total_jam = 0
            status_log = "Belum membuat log"  # karena log belum dibuat

        hasil.append({
            'nama': mhs.nama,
            'npm': mhs.npm,
            'program': program,
            'tanggal_mulai': tanggal_mulai,
            'tanggal_selesai': tanggal_selesai,
            'status': status_log,
        })

    # Ambil PA yang sesuai dengan user
    # pa_instance = PembimbingAkademik.objects.filter(user=user).first()

    # Jika user adalah PA dan ada PA terkait, filter berdasarkan PA
    # if is_pa(user) and not (is_dosen(user) or is_kaprodi(user)) and pa_instance:
    #     mahasiswa = mahasiswa.filter(pa=pa_instance)
    # elif is_pa(user) and pa_instance:
    #     mahasiswa = mahasiswa.filter(
    #         Q(pa=pa_instance) | Q(pendaftarankp__semester=semester) | Q(pendaftaranmbkm__semester=semester)
    #     ).distinct()

    # Menerapkan filter tambahan dari django-filters
    # mahasiswa_filter = MahasiswaFilter(request.GET, queryset=mahasiswa)

    return render(request, 'list_mahasiswa_ke_log.html', {
        'semester': semester,
        'hasil_log': hasil
    })
