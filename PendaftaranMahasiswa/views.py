from django.shortcuts import render
from database.models import PendaftaranMBKM, PendaftaranKP, Semester

def daftar_program(request):
    mahasiswa = request.user.mahasiswa
    semester_aktif = Semester.objects.filter(aktif=True).first()
    # Cek pendaftaran yang sudah ada
    pendaftaran_kp = PendaftaranKP.objects.filter(
        mahasiswa=mahasiswa, 
        semester=semester_aktif
    ).first()
    
    pendaftaran_mbkm = PendaftaranMBKM.objects.filter(
        mahasiswa=mahasiswa, 
        semester=semester_aktif
    ).first()

    context = {
        'pendaftaran_kp': pendaftaran_kp,
        'pendaftaran_mbkm': pendaftaran_mbkm
    }
    
    return render(request, 'daftar_program.html', context)