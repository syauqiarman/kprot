from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from PendaftaranMahasiswaKP.forms import PendaftaranKPForm
from database.models import PendaftaranKP, Semester

@login_required
def daftar_kp(request):
    mahasiswa = request.user.mahasiswa
    semester_aktif = Semester.objects.filter(aktif=True).first()

    # Ambil data pendaftaran yang sudah ada
    existing_pendaftaran = PendaftaranKP.objects.filter(
        mahasiswa=mahasiswa, 
        semester=semester_aktif
    ).first()

    if existing_pendaftaran:
        return render(request, 'daftar_kp_gagal.html', {
            'message': 'Anda sudah melakukan pendaftaran program KP di semester ini.',
            'pendaftaran': existing_pendaftaran  # Kirim objek pendaftaran
        })
    
    if request.method == 'POST':
        form = PendaftaranKPForm(request.POST, user=request.user)
        if form.is_valid():
            pendaftaran = form.save(commit=False)
            pendaftaran.mahasiswa = request.user.mahasiswa
            pendaftaran.save()
            return redirect("PendaftaranMahasiswaKP:kp_berhasil", pendaftaran_id=pendaftaran.id) 
    else:
        form = PendaftaranKPForm(user=request.user)
    
    return render(request, 'pendaftaran_kp.html', {'form': form})

@login_required
def kp_berhasil(request, pendaftaran_id):
    pendaftaran = PendaftaranKP.objects.get(id=pendaftaran_id)
    return render(request, 'daftarkp_berhasil.html', {'pendaftaran': pendaftaran})