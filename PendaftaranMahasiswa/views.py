from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PendaftaranKPForm
from .models import PendaftaranKP

@login_required
def daftar_kp(request):
    if request.method == 'POST':
        form = PendaftaranKPForm(request.POST, user=request.user)
        if form.is_valid():
            # Simpan data pendaftaran
            pendaftaran = form.save(commit=False)
            pendaftaran.mahasiswa = request.user.mahasiswa
            pendaftaran.save()
            return redirect("PendaftaranMahasiswa:kp_berhasil", pendaftaran_id=pendaftaran.id)  # Kirim ID pendaftaran ke halaman sukses
    else:
        form = PendaftaranKPForm(user=request.user)
    
    return render(request, 'pendaftaran_kp.html', {'form': form})

@login_required
def kp_berhasil(request, pendaftaran_id):
    # Ambil data pendaftaran berdasarkan ID
    pendaftaran = PendaftaranKP.objects.get(id=pendaftaran_id)
    return render(request, 'daftar_berhasil.html', {'pendaftaran': pendaftaran})