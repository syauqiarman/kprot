from django.shortcuts import render
from database.models import PendaftaranMBKM, PendaftaranKP, Semester

def daftar_program(request):
    mahasiswa = request.user.mahasiswa
    semester_aktif = Semester.objects.filter(aktif=True).first()
    # Cek pendaftaran yang sudah ada
    sudah_daftar_kp = PendaftaranKP.objects.filter(
        mahasiswa=mahasiswa, 
        semester=semester_aktif
    ).exists()
    
    sudah_daftar_mbkm = PendaftaranMBKM.objects.filter(
        mahasiswa=mahasiswa, 
        semester=semester_aktif
    ).exists()

    context = {
        'sudah_daftar_kp': sudah_daftar_kp,
        'sudah_daftar_mbkm': sudah_daftar_mbkm
    }
    
    return render(request, 'daftar_program.html', context)