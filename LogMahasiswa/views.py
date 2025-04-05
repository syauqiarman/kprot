from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import LogMingguanForm, AktivitasHarianFormSet
from database.models import LogMingguan, PendaftaranKP, PendaftaranMBKM

@login_required
def buat_log(request):
    mahasiswa = request.user.mahasiswa
    program_kp = PendaftaranKP.objects.filter(mahasiswa=mahasiswa, status_pendaftaran='Terdaftar').first()
    program_mbkm = PendaftaranMBKM.objects.filter(mahasiswa=mahasiswa, status_pendaftaran='Terdaftar').first()
    
    if not program_kp and not program_mbkm:
        return render(request, 'log/error.html', {'message': 'Anda belum terdaftar di program KP atau MBKM yang aktif.'})
    
    if request.method == 'POST':
        form = LogMingguanForm(request.POST, user=request.user)
        formset = AktivitasHarianFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            log_mingguan = form.save()
            formset.instance = log_mingguan
            formset.save()
            return redirect('LogMahasiswa:daftar_log')
    else:
        form = LogMingguanForm(user=request.user)
        formset = AktivitasHarianFormSet(instance=None)
    
    return render(request, 'log/buat_log.html', {
        'form': form,
        'formset': formset,
        'program_kp': program_kp,
        'program_mbkm': program_mbkm,
    })

@login_required
def daftar_log(request):
    mahasiswa = request.user.mahasiswa
    logs_kp = LogMingguan.objects.filter(pendaftaran_kp__mahasiswa=mahasiswa)
    logs_mbkm = LogMingguan.objects.filter(pendaftaran_mbkm__mahasiswa=mahasiswa)
    logs = list(logs_kp) + list(logs_mbkm)
    logs.sort(key=lambda x: x.tanggal_mulai, reverse=True)
    
    total_jam_keseluruhan = sum(log.total_jam_mingguan for log in logs)
    
    return render(request, 'log/daftar_log.html', {
        'logs': logs,
        'total_jam_keseluruhan': total_jam_keseluruhan,
    })

@login_required
def detail_log(request, log_id):
    log = get_object_or_404(LogMingguan, id=log_id)
    if (log.pendaftaran_kp and log.pendaftaran_kp.mahasiswa != request.user.mahasiswa) or \
       (log.pendaftaran_mbkm and log.pendaftaran_mbkm.mahasiswa != request.user.mahasiswa):
        return redirect('LogMahasiswa:daftar_log')
    
    aktivitas_harian = log.aktivitas_harian.all()
    return render(request, 'log/detail_log.html', {
        'log': log,
        'aktivitas_harian': aktivitas_harian,
        'total_jam_mingguan': log.total_jam_mingguan,
    })

@login_required
def edit_log(request, log_id):
    log = get_object_or_404(LogMingguan, id=log_id)
    if (log.pendaftaran_kp and log.pendaftaran_kp.mahasiswa != request.user.mahasiswa) or \
       (log.pendaftaran_mbkm and log.pendaftaran_mbkm.mahasiswa != request.user.mahasiswa):
        return redirect('LogMahasiswa:daftar_log')
    
    if request.method == 'POST':
        form = LogMingguanForm(request.POST, instance=log, user=request.user)
        formset = AktivitasHarianFormSet(request.POST, instance=log)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('LogMahasiswa:detail_log', log_id=log.id)
    else:
        form = LogMingguanForm(instance=log, user=request.user)
        formset = AktivitasHarianFormSet(instance=log)
    
    return render(request, 'log/edit_log.html', {
        'form': form,
        'formset': formset,
        'log': log,
    })

@login_required
def hapus_log(request, log_id):
    log = get_object_or_404(LogMingguan, id=log_id)
    if (log.pendaftaran_kp and log.pendaftaran_kp.mahasiswa != request.user.mahasiswa) or \
       (log.pendaftaran_mbkm and log.pendaftaran_mbkm.mahasiswa != request.user.mahasiswa):
        return redirect('LogMahasiswa:daftar_log')
    
    if request.method == 'POST':
        log.delete()
        return redirect('LogMahasiswa:daftar_log')
    
    return render(request, 'log/hapus_log.html', {'log': log})