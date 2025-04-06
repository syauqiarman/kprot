from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from database.models import LogMingguan, PendaftaranKP, PendaftaranMBKM
from django.db import models
from django.db.models import Sum
from .forms import LogMingguanForm, AktivitasHarianFormSet

def create_log(request):
    try:
        program = PendaftaranKP.objects.get(
            mahasiswa__user=request.user,
            status_pendaftaran='Terdaftar'
        )
    except PendaftaranKP.DoesNotExist:
        try:
            program = PendaftaranMBKM.objects.get(
                mahasiswa__user=request.user,
                status_pendaftaran='Terdaftar'
            )
        except PendaftaranMBKM.DoesNotExist:
            messages.warning(request, "Anda belum memiliki program yang aktif")
            return redirect(request.META.get('HTTP_REFERER', '/'))

    if request.method == 'POST':
        form = LogMingguanForm(request.POST, program=program)
        
        if form.is_valid():
            # Simpan log terlebih dahulu
            log = form.save(commit=False)
            if isinstance(program, PendaftaranKP):
                log.pendaftaran_kp = program
            else:
                log.pendaftaran_mbkm = program
            log.save()  # Simpan untuk mendapatkan ID
            
            # Sekarang proses formset dengan instance yang sudah ada
            formset = AktivitasHarianFormSet(request.POST, instance=log)
            if formset.is_valid():
                formset.save()

                log.total_jam = log.calculate_total_jam()
                log.save()
                
                messages.success(request, "Log mingguan berhasil disimpan!")
                return redirect('LogMahasiswa:log_detail')
            else:
                # Hapus log jika formset tidak valid
                log.delete()
                messages.error(request, "Terjadi kesalahan pada aktivitas harian")
        else:
            formset = AktivitasHarianFormSet()
    else:
        form = LogMingguanForm(program=program)
        formset = AktivitasHarianFormSet()

    return render(request, 'log_form.html', {
        'form': form,
        'formset': formset,
        'program': program
    })

def log_detail(request):
    try:
        program = PendaftaranKP.objects.get(
            mahasiswa__user=request.user,
            status_pendaftaran='Terdaftar'
        )
    except PendaftaranKP.DoesNotExist:
        try:
            program = PendaftaranMBKM.objects.get(
                mahasiswa__user=request.user,
                status_pendaftaran='Terdaftar'
            )
        except PendaftaranMBKM.DoesNotExist:
            messages.warning(request, "Anda belum memiliki program yang aktif")
            return redirect('LogMahasiswa:create_log')
    
    # Ambil semua log terkait program
    if isinstance(program, PendaftaranKP):
        logs = LogMingguan.objects.filter(pendaftaran_kp=program).order_by('-tanggal_mulai')
    else:
        logs = LogMingguan.objects.filter(pendaftaran_mbkm=program).order_by('-tanggal_mulai')
    
    # Hitung total jam dari semua log
    total_jam = logs.aggregate(total=Sum('total_jam'))['total'] or 0.0
    
    return render(request, 'log_detail.html', {
        'program': program,
        'logs': logs,
        'total_jam': total_jam
    })