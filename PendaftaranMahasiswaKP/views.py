from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from PendaftaranMahasiswaKP.forms import PendaftaranKPForm
from database.models import PendaftaranKP, Semester

@login_required
def daftar_kp(request):
    mahasiswa = request.user.mahasiswa
    semester_aktif = Semester.objects.filter(aktif=True).first()

    if PendaftaranKP.objects.filter(mahasiswa=mahasiswa, semester=semester_aktif).exists():
        return render(request, 'daftar_kp_gagal.html', {'message': 'Anda sudah mendaftar KP di semester ini.'})
    
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

@login_required
def daftar_kp_gagal(request):
    return render(request, 'daftar_kp_gagal.html')