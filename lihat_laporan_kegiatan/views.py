from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from input_detil.models import Penyelia, PendaftaranKP, PendaftaranMBKM, LaporanKP, LaporanMBKM, Mahasiswa, Semester

# Create your views here.
@login_required
@require_GET
def lihat_laporan_kegiatan(request, program, mahasiswa_id, pendaftaran_id):
    mahasiswa = get_object_or_404(Mahasiswa, id=mahasiswa_id)
    # check if user penyelia
    if not is_penyelia(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
  
    pendaftaran = None
    if program == 'kp':
        pendaftaran = get_object_or_404(PendaftaranKP, id=pendaftaran_id)
    elif program == 'mbkm':
        pendaftaran = get_object_or_404(PendaftaranMBKM, id=pendaftaran_id)
    else:
        return JsonResponse({'error': 'Invalid program'}, status=404)
    
    # fetch laporan
    laporan = fetch_laporan(pendaftaran_id, program)
    
    context = {
        'laporan': laporan,
        'pendaftaran': pendaftaran,
        'program': program,
    }

    return render(request, 'lihat_laporan_kegiatan.html', context)

# temporary dashboard for penyelia
@login_required
@require_GET
def temp_dashboard_penyelia(request):
    if not Penyelia.objects.filter(user=request.user).exists():
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    # ambil semua pendaftaran KP dan MBKM dari penyelia tersebut
    kp_list = PendaftaranKP.objects.filter(penyelia__user=request.user)
    mbkm_list = PendaftaranMBKM.objects.filter(penyelia__user=request.user)

    context = {
        "kp_list": kp_list,
        "mbkm_list": mbkm_list,
    }
    
    return render(request, "temp_dashboard_penyelia.html", context)

@login_required
@require_POST
def persetujuan_laporan(request, program, id_mahasiswa):
    action = request.POST.get('action')
    feedback = request.POST.get('feedback', '')

    mahasiswa = get_object_or_404(Mahasiswa, id=id_mahasiswa)
    semester_aktif = Semester.objects.filter(aktif=True).first()

    # Ambil pendaftaran sesuai program
    if program == 'kp':
        pendaftaran = PendaftaranKP.objects.filter(mahasiswa=mahasiswa).first()
    elif program == 'mbkm':
        pendaftaran = PendaftaranMBKM.objects.filter(mahasiswa=mahasiswa).first()
    else:
        messages.error(request, 'Program tidak valid.')
        return redirect(request.META.get('HTTP_REFERER', reverse('lihat_laporan_kegiatan:temp_dashboard_penyelia')))

    if pendaftaran is None:
        messages.error(request, 'Pendaftaran tidak ditemukan.')
        return redirect(request.META.get('HTTP_REFERER', reverse('lihat_laporan_kegiatan:temp_dashboard_penyelia')))

    # Cek apakah semester pendaftaran adalah semester aktif
    if not semester_aktif or pendaftaran.semester != semester_aktif:
        messages.error(request, 'Persetujuan hanya dapat dilakukan pada semester aktif.')
        # return redirect(request.META.get('HTTP_REFERER'))
        return redirect(request.META.get('HTTP_REFERER', reverse('lihat_laporan_kegiatan:temp_dashboard_penyelia')))

    laporan = fetch_laporan(pendaftaran.id, program)
    if laporan is None:
        messages.error(request, 'Laporan tidak ditemukan.')
        return redirect(request.META.get('HTTP_REFERER', reverse('lihat_laporan_kegiatan:temp_dashboard_penyelia')))

    if action == 'approve':
        laporan.status_persetujuan_penyelia = 'Disetujui'
        laporan.save()
        messages.success(request, 'Laporan disetujui.')
    elif action == 'reject':
        if not feedback.strip():
            messages.error(request, 'Feedback harus diisi saat menolak laporan.')
            return redirect(request.META.get('HTTP_REFERER'))
        laporan.status_persetujuan_penyelia = 'Ditolak'
        laporan.feedback_penolakan_penyelia = feedback
        laporan.save()
        messages.success(request, 'Laporan ditolak dengan feedback.')
    else:
        messages.error(request, 'Aksi tidak valid.')

    return redirect(request.META.get('HTTP_REFERER', reverse('lihat_laporan_kegiatan:temp_dashboard_penyelia')))


# decorator design pattern
def is_penyelia(user):
    return Penyelia.objects.filter(user=user).exists()

def fetch_laporan(pendaftaran_id, program):
    if program == 'kp':
        this_laporan = LaporanKP.objects.filter(pendaftaran__id=pendaftaran_id).first()
    elif program == 'mbkm':
        this_laporan = LaporanMBKM.objects.filter(pendaftaran__id=pendaftaran_id).first()
    
    return this_laporan