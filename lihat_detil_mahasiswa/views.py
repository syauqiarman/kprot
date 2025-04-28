from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from testapp.models import PendaftaranKP, PendaftaranMBKM, Semester, Mahasiswa, Manajemen, PembimbingAkademik, Dosen, Manajemen

ROLE_STATUS = {
    Manajemen: "Menunggu Persetujuan Manajemen",
    PembimbingAkademik: "Menunggu Persetujuan PA",
    Dosen: "Menunggu Verifikasi Dosen",
}

REJECTION_STATUS = {
    Manajemen: "Ditolak Manajemen",
    PembimbingAkademik: "Ditolak PA",
    Dosen: "Ditolak Dosen",
}

@login_required
@require_GET
def pendaftaran_kp_by_mahasiswa(request, mahasiswa_id, semester_id=None):
    mahasiswa = get_object_or_404(Mahasiswa, id=mahasiswa_id)
    if not user_can_access_mahasiswa(request.user, mahasiswa):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if semester_id: 
        semester = get_object_or_404(Semester, id=semester_id)
    else:
        semester = get_object_or_404(Semester, aktif=True)

    pendaftaran = get_object_or_404(PendaftaranKP, mahasiswa=mahasiswa, semester=semester)

    semua_pendaftaran = [(p.semester.nama, 'MBKM', p.semester.tahun, p.semester.gasal_genap, p.semester.id) for p in PendaftaranMBKM.objects.filter(mahasiswa=mahasiswa)] + \
                        [(p.semester.nama, 'KP', p.semester.tahun, p.semester.gasal_genap, p.semester.id) for p in PendaftaranKP.objects.filter(mahasiswa=mahasiswa) if p.semester != semester]
    
    semua_pendaftaran = sorted(semua_pendaftaran, key=lambda x: (x[2], x[3]), reverse=True)

    data = {
        "id": pendaftaran.pk,
        "nama_mahasiswa": pendaftaran.mahasiswa.nama,
        "npm_mahasiswa": pendaftaran.mahasiswa.npm,
        "id_mahasiswa": pendaftaran.mahasiswa.id,
        "semester": pendaftaran.semester.nama,
        "jumlah_semester": pendaftaran.jumlah_semester,
        "sks_lulus": pendaftaran.sks_lulus,
        "penyelia": pendaftaran.penyelia.nama if pendaftaran.penyelia else None,
        "perusahaan": pendaftaran.penyelia.perusahaan,
        "role": pendaftaran.role,
        "total_jam_kerja": pendaftaran.total_jam_kerja,
        "tanggal_mulai": pendaftaran.tanggal_mulai,
        "tanggal_selesai": pendaftaran.tanggal_selesai,
        "pernyataan_komitmen": pendaftaran.pernyataan_komitmen,
        "status_pendaftaran": pendaftaran.status_pendaftaran,
        "semua_pendaftaran": semua_pendaftaran,
        "dashboard_url": "/home_mahasiswa/" 
                         if Mahasiswa.objects.filter(user=request.user).exists()
                         else "/home_others/",
        "pendaftaran_url": f"/detil/pendaftaran/kp/{mahasiswa_id}/{semester_id}/" 
                           if Mahasiswa.objects.filter(user=request.user).exists()
                           else "/listmahasiswa/listsemester/",
    }
    return render(request, 'detil_pendaftaran_kp.html', data)

@login_required
@require_GET
def pendaftaran_mbkm_by_mahasiswa(request, mahasiswa_id, semester_id=None):
    mahasiswa = get_object_or_404(Mahasiswa, id=mahasiswa_id)
    if not user_can_access_mahasiswa(request.user, mahasiswa):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if semester_id:
        semester = get_object_or_404(Semester, id=semester_id)
    else:
        semester = get_object_or_404(Semester, aktif=True)

    pendaftaran = get_object_or_404(PendaftaranMBKM, mahasiswa=mahasiswa, semester=semester)

    semua_pendaftaran = [(p.semester.nama, 'MBKM', p.semester.tahun, p.semester.gasal_genap, p.semester.id) for p in PendaftaranMBKM.objects.filter(mahasiswa=mahasiswa) if p.semester != semester] + \
                        [(p.semester.nama, 'KP', p.semester.tahun, p.semester.gasal_genap, p.semester.id) for p in PendaftaranKP.objects.filter(mahasiswa=mahasiswa)]
    
    semua_pendaftaran = sorted(semua_pendaftaran, key=lambda x: (x[2], x[3]), reverse=True)

    data = {
        "is_pa": PembimbingAkademik.objects.filter(user=request.user).exists(),
        "is_Manajemen": Manajemen.objects.filter(user=request.user).exists(), 
        "is_dosen": Dosen.objects.filter(user=request.user).exists(),
        "id": pendaftaran.pk,
        "nama_mahasiswa": pendaftaran.mahasiswa.nama,
        "npm_mahasiswa": pendaftaran.mahasiswa.npm,
        "id_mahasiswa": pendaftaran.mahasiswa.id,
        "semester": pendaftaran.semester.nama,
        "jumlah_semester": pendaftaran.jumlah_semester,
        "sks_diambil": pendaftaran.sks_diambil,
        "rencana_lulus_semester_ini": pendaftaran.rencana_lulus_semester_ini,
        "program_mbkm": pendaftaran.program_mbkm.nama,
        "penyelia": pendaftaran.penyelia.nama if pendaftaran.penyelia else None,
        "perusahaan": pendaftaran.penyelia.perusahaan,
        "role": pendaftaran.role,
        "estimasi_sks_konversi": pendaftaran.estimasi_sks_konversi,
        "persetujuan_pa": pendaftaran.persetujuan_pa.url if pendaftaran.persetujuan_pa else None,
        "tanggal_persetujuan": pendaftaran.tanggal_persetujuan,
        "tanggal_mulai": pendaftaran.tanggal_mulai,
        "tanggal_selesai": pendaftaran.tanggal_selesai,
        "status_pendaftaran": pendaftaran.status_pendaftaran,
        "feedback_penolakan":pendaftaran.feedback_penolakan,
        "semua_pendaftaran": semua_pendaftaran,
        "dashboard_url": "/home_mahasiswa/" 
                         if Mahasiswa.objects.filter(user=request.user).exists()
                         else "/home_others/",
        "pendaftaran_url": f"/detil/pendaftaran/mbkm/{mahasiswa_id}/{semester_id}/" 
                           if Mahasiswa.objects.filter(user=request.user).exists()
                           else "/listmahasiswa/listsemester/",
    }
    return render(request, 'detil_pendaftaran_mbkm.html', data)

@login_required
@require_POST
def approve_reject_pendaftaran_mbkm(request, pendaftaran_id, action):
    pendaftaran = get_object_or_404(PendaftaranMBKM, id=pendaftaran_id)
    user = request.user
    if not user_can_access_mahasiswa(user, pendaftaran.mahasiswa):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    valid = False
    for role in [Manajemen, PembimbingAkademik, Dosen]:
        if role.objects.filter(user=user).exists() and pendaftaran.status_pendaftaran == ROLE_STATUS[role]:
            response = approve_reject_pendaftaran_mbkm_by_role(action, request, pendaftaran, role)
            valid = True
            break

    if not valid:
        return JsonResponse({"error": "Unauthorized action"}, status=403)
    if response:
        return response
    
    return redirect(request.META.get('HTTP_REFERER', reverse('admin:index')))  # Redirect back or to a default view


############################################# Helper Functions #############################################

def user_can_access_mahasiswa(user, mahasiswa):
    return Dosen.objects.filter(user=user).exists() or \
           Manajemen.objects.filter(user=user).exists() or \
           ManajemenFakultas.objects.filter(user=user).exists() or \
           (mahasiswa.pa and mahasiswa.pa.user == user) or \
           user.is_superuser or \
           mahasiswa.user == user

def approve_reject_pendaftaran_mbkm_by_role(action, request, pendaftaran, role):
    if action == "approve":
        pendaftaran.status_pendaftaran = "Terdaftar" if role is Manajemen else "Menunggu Persetujuan Manajemen"
        pendaftaran.save()

    elif action == "reject":
        feedback_penolakan = request.POST.get('feedback_penolakan')
        if not feedback_penolakan:
            return JsonResponse({"error": "Feedback penolakan harus diisi"}, status=400)
        
        pendaftaran.status_pendaftaran = REJECTION_STATUS[role]
        pendaftaran.feedback_penolakan = feedback_penolakan
        pendaftaran.save()

    else:
        return JsonResponse({"error": "Unauthorized action"}, status=403)