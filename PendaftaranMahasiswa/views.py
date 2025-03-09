from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Mahasiswa, PendaftaranMBKM
from .forms import PendaftaranMBKMForm

@login_required
def daftar_mbkm(request):
    try:
        mahasiswa = Mahasiswa.objects.get(user=request.user)
    except Mahasiswa.DoesNotExist:
        messages.error(request, "Anda bukan mahasiswa yang berhak mendaftar.")
        return redirect('home')

    if mahasiswa.jumlah_semester < 5:
        messages.warning(request, "Anda belum memenuhi syarat untuk mendaftar MBKM.")
        return redirect('home')

    if request.method == "POST":
        form = PendaftaranMBKMForm(request.POST, mahasiswa=mahasiswa)
        if form.is_valid():
            pendaftaran = form.save(commit=False)
            pendaftaran.mahasiswa = mahasiswa
            pendaftaran.semester = mahasiswa.semester
            pendaftaran.status_pendaftaran = "Berencana Mendaftar MBKM"
            pendaftaran.save()
            messages.success(request, "Pendaftaran berhasil! Status Anda: Berencana Mendaftar MBKM.")
            return redirect('home')
    else:
        form = PendaftaranMBKMForm(mahasiswa=mahasiswa)

    return render(request, 'PendaftaranMahasiswa/daftar_mbkm.html', {'form': form})
