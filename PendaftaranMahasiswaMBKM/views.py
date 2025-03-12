from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from PendaftaranMahasiswaMBKM.forms import PendaftaranMBKMForm
from database.models import PendaftaranMBKM, Semester

@login_required
def daftar_mbkm(request):
    mahasiswa = request.user.mahasiswa
    semester_aktif = Semester.objects.filter(aktif=True).first()

    if PendaftaranMBKM.objects.filter(mahasiswa=mahasiswa, semester=semester_aktif).exists():
        return render(request, 'daftar_mbkm_gagal.html', {'message': 'Anda sudah mendaftar MBKM di semester ini.'})
    
    if request.method == 'POST':
        form = PendaftaranMBKMForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            # Simpan data pendaftaran
            pendaftaran = form.save(commit=False)
            pendaftaran.mahasiswa = request.user.mahasiswa
            pendaftaran.save()
            return redirect('PendaftaranMahasiswaMBKM:daftar_berhasil', pendaftaran_id=pendaftaran.id)  # Kirim ID pendaftaran ke halaman sukses
    else:
        form = PendaftaranMBKMForm(user=request.user)
    
    return render(request, 'daftar_mbkm.html', {'form': form})

@login_required
def daftar_berhasil(request, pendaftaran_id):
    # Ambil data pendaftaran berdasarkan ID
    pendaftaran = PendaftaranMBKM.objects.get(id=pendaftaran_id)
    return render(request, 'daftarmbkm_berhasil.html', {'pendaftaran': pendaftaran})

@login_required
def daftar_mbkm_gagal(request):
    return render(request, 'daftar_mbkm_gagal.html')