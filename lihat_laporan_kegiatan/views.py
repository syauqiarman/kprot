# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required
# from input_detil.models import LaporanKP, LaporanMBKM
# from lihat_laporan_kegiatan.forms import PersetujuanLaporanForm

# def get_latest_laporan(penyelia):
#     """Mengambil laporan terbaru mahasiswa yang dibimbing oleh penyelia."""
#     # laporan_kp = LaporanKP.objects.filter(mahasiswa__penyelia=penyelia).order_by('-tanggal_pengajuan')
#     laporan_kp = LaporanKP.objects.filter(mahasiswa__penyelia=penyelia).order_by('-tanggal_pengajuan')
#     laporan_mbkm = LaporanMBKM.objects.filter(mahasiswa__penyelia=penyelia).order_by('-tanggal_pengajuan')
#     return {'laporan_kp': laporan_kp, 'laporan_mbkm': laporan_mbkm}

# # @login_required
# def daftar_laporan(request):
#     penyelia = request.user.penyelia
#     laporan = get_latest_laporan(penyelia)
#     return render(request, 'laporan/daftar_laporan.html', {'laporan': laporan})

# # @login_required
# def persetujuan_laporan(request, laporan_id, jenis):
#     if jenis == 'kp':
#         laporan = get_object_or_404(LaporanKP, id=laporan_id)
#     else:
#         laporan = get_object_or_404(LaporanMBKM, id=laporan_id)

#     if request.method == 'POST':
#         form = PersetujuanLaporanForm(request.POST, instance=laporan)
#         if form.is_valid():
#             laporan = form.save(commit=False)
#             if not laporan.disetujui_penyelia:
#                 laporan.disetujui_dosen = False  # Jika ditolak penyelia, dosen tidak bisa menyetujui
#             laporan.save()
#             return redirect('daftar_laporan')
#     else:
#         form = PersetujuanLaporanForm(instance=laporan)

#     return render(request, 'laporan/persetujuan_laporan.html', {'form': form, 'laporan': laporan})

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from input_detil.models import Penyelia, PendaftaranKP, PendaftaranMBKM, Laporan, LaporanKP, LaporanMBKM, Mahasiswa

# Create your views here.
@login_required
@require_GET
def lihat_laporan_kegiatan(request, program, mahasiswa_id):
    mahasiswa = get_object_or_404(Mahasiswa, id=mahasiswa_id)
    
    # check if user penyelia
    if not is_penyelia(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # fetch laporan
    laporan = fetch_laporan(mahasiswa_id, program)
  
    # get pendaftaran
    pendaftaran = None
    if program == 'kp':
        pendaftaran = get_object_or_404(PendaftaranKP, mahasiswa=mahasiswa)
    elif program == 'mbkm':
        pendaftaran = get_object_or_404(PendaftaranMBKM, mahasiswa=mahasiswa)
    
    context = {
        'laporan': laporan,
        'pendaftaran': pendaftaran,
        'program': program,
    }

    return render(request, 'lihat_laporan_kegiatan.html', context)

# decorator design pattern
def is_penyelia(user):
    return Penyelia.objects.filter(user=user).exists()

def fetch_laporan(mahasiswa_id, program):
    if program == 'kp':
        this_laporan = LaporanKP.objects.filter(pendaftaran__mahasiswa__id=mahasiswa_id).first()
    elif program == 'mbkm':
        this_laporan = LaporanMBKM.objects.filter(pendaftaran__mahasiswa__id=mahasiswa_id).first()
    
    return this_laporan

@login_required
def dashboard_penyelia_sementara(request):
    if not Penyelia.objects.filter(user=request.user).exists():
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    # ambil semua pendaftaran KP dan MBKM dari penyelia tersebut
    kp_list = PendaftaranKP.objects.filter(penyelia__user=request.user)
    mbkm_list = PendaftaranMBKM.objects.filter(penyelia__user=request.user)

    context = {
        "kp_list": kp_list,
        "mbkm_list": mbkm_list,
    }

    return render(request, "dashboard_penyelia_sementara.html", context)

def persetujuan_laporan():
    return None
