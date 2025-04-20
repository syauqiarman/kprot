from datetime import datetime, timedelta
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect
from django.contrib import messages
from database.models import Aktivitas, Hari, LogMingguan, PendaftaranKP, PendaftaranMBKM
from django.db.models import Sum
from LogMahasiswa.forms import AktivitasForm, LogMingguanForm, HariFormSet, AktivitasFormSet

def create_log(request):
    try:
        program = PendaftaranKP.objects.get(
            mahasiswa__user=request.user,
            status_pendaftaran='Terdaftar',
            semester__aktif=True
        )
    except PendaftaranKP.DoesNotExist:
        try:
            program = PendaftaranMBKM.objects.get(
                mahasiswa__user=request.user,
                status_pendaftaran='Terdaftar',
                semester__aktif=True
            )
        except PendaftaranMBKM.DoesNotExist:
            messages.warning(request, "Anda belum memiliki program yang aktif")
            return redirect('home_mahasiswa')

    if request.method == 'POST':
        form = LogMingguanForm(request.POST, program=program)
        if form.is_valid():
            log = form.save(commit=False)
            
            # Assign program
            if isinstance(program, PendaftaranKP):
                log.pendaftaran_kp = program
            else:
                log.pendaftaran_mbkm = program
            
            # Simpan pertama kali untuk mendapatkan PK
            log.save()
            
            # Buat hari-hari
            start_date = form.cleaned_data['tanggal_mulai']
            end_date = form.cleaned_data['tanggal_selesai']
            delta = (end_date - start_date).days + 1
            hari_list = []
            
            for i in range(delta):
                current_date = start_date + timedelta(days=i)
                hari = Hari.objects.create(
                    log_mingguan=log,
                    tanggal=current_date
                )
                hari_list.append(hari)
            
            total_jam = 0
            
            # Proses aktivitas untuk setiap hari
            for i, hari in enumerate(hari_list):
                AktivitasFormSet = inlineformset_factory(
                    Hari,
                    Aktivitas,
                    form=AktivitasForm,
                    extra=0,
                    can_delete=True,
                    min_num=1,
                    validate_min=True
                )
                
                aktivitas_formset = AktivitasFormSet(
                    request.POST,
                    instance=hari,
                    prefix=f'day-{i}'
                )
                
                if aktivitas_formset.is_valid():
                    aktivitas_instances = aktivitas_formset.save(commit=False)
                    for aktivitas in aktivitas_instances:
                        aktivitas.hari = hari  # Pastikan relasi terisi
                        aktivitas.save()
                        total_jam += aktivitas.durasi
                else:
                    log.delete()
                    messages.error(request, f"Error di hari ke-{i+1}: {aktivitas_formset.errors}")
                    return redirect('LogMahasiswa:create_log')
            
            # Update total jam
            log.total_jam = total_jam
            log.save()
            
            messages.success(request, "Log berhasil disimpan!")
            return redirect('LogMahasiswa:log_detail')
        else:
            messages.error(request, "Terjadi kesalahan pada form log")
    else:
        form = LogMingguanForm(program=program)
    
    return render(request, 'log_form.html', {
        'form': form,
        'program': program,
    })

def log_detail(request):
    try:
        program = PendaftaranKP.objects.get(
            mahasiswa__user=request.user,
            status_pendaftaran='Terdaftar',
            semester__aktif=True
        )
    except PendaftaranKP.DoesNotExist:
        try:
            program = PendaftaranMBKM.objects.get(
                mahasiswa__user=request.user,
                status_pendaftaran='Terdaftar',
                semester__aktif=True
            )
        except PendaftaranMBKM.DoesNotExist:
            messages.warning(request, "Anda belum memiliki program yang aktif")
            return redirect(request.META.get('HTTP_REFERER', '/'))
    
    # Ambil semua log terkait program
    if isinstance(program, PendaftaranKP):
        logs = LogMingguan.objects.filter(pendaftaran_kp=program).order_by('-tanggal_mulai')
    else:
        logs = LogMingguan.objects.filter(pendaftaran_mbkm=program).order_by('-tanggal_mulai')
    
    if not logs.exists():
        messages.info(request, "Belum ada log mingguan yang tercatat.")

    # Hitung total jam dari semua log
    total_jam = sum(log.calculate_total_jam() for log in logs)
    
    return render(request, 'log_detail.html', {
        'program': program,
        'logs': logs,
        'total_jam': total_jam
    })