from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from database.models import PendaftaranKP, PendaftaranMBKM, LogMingguan
from LogMahasiswa.forms import LogMingguanForm, AktivitasFormSet

@login_required
def buat_log(request):
    mahasiswa = request.user.mahasiswa
    program_kp = PendaftaranKP.objects.filter(mahasiswa=mahasiswa, status_pendaftaran='Terdaftar').first()
    program_mbkm = PendaftaranMBKM.objects.filter(mahasiswa=mahasiswa, status_pendaftaran='Terdaftar').first()
    program = program_kp or program_mbkm

    if not program:
        return render(request, 'error.html', {'message': 'Anda tidak memiliki program aktif'})

    if request.method == 'POST':
        form = LogMingguanForm(request.POST, program=program)
        formset = AktivitasFormSet(request.POST)
        
        if form.is_valid():
            # Simpan log terlebih dahulu
            log = form.save(commit=False)
            if program_kp:
                log.program_kp = program_kp
            else:
                log.program_mbkm = program_mbkm
            log.save()
            
            # Hubungkan formset dengan log yang sudah disimpan
            formset = AktivitasFormSet(request.POST, instance=log)
            
            if formset.is_valid():
                formset.save()
                return redirect('LogMahasiswa:daftar_log')
    else:
        form = LogMingguanForm(program=program)
        formset = AktivitasFormSet()

    return render(request, 'buat_log.html', {
        'form': form,
        'formset': formset,
        'program': program,
    })

@login_required
def daftar_log(request):
    mahasiswa = request.user.mahasiswa
    logs_kp = LogMingguan.objects.filter(program_kp__mahasiswa=mahasiswa)
    logs_mbkm = LogMingguan.objects.filter(program_mbkm__mahasiswa=mahasiswa)
    logs = list(logs_kp) + list(logs_mbkm)
    logs.sort(key=lambda x: x.tanggal_mulai, reverse=True)
    
    total_jam = sum(log.total_jam_mingguan for log in logs)
    
    return render(request, 'daftar_log.html', {
        'logs': logs,
        'total_jam': total_jam,
    })