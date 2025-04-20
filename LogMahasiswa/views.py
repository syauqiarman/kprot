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
            return redirect(request.META.get('HTTP_REFERER', '/'))

    if request.method == 'POST':
        form = LogMingguanForm(request.POST, program=program)
        
        if form.is_valid():
            log = form.save(commit=False)
            if isinstance(program, PendaftaranKP):
                log.pendaftaran_kp = program
            else:
                log.pendaftaran_mbkm = program
            log.save()

            # Create hari objects first
            start_date = form.cleaned_data['tanggal_mulai']
            end_date = form.cleaned_data['tanggal_selesai']
            delta = (end_date - start_date).days + 1
            
            # Create all hari objects
            hari_list = []
            for i in range(delta):
                current_date = start_date + timedelta(days=i)
                hari = Hari.objects.create(
                    log_mingguan=log,
                    tanggal=current_date
                )
                hari_list.append(hari)

            total_jam = 0
            # Process activities for each day
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
                    aktivitas_formset.save()
                    # Hitung total jam
                    for aktivitas in aktivitas_formset.save(commit=False):
                        if not aktivitas.pk:  # Hanya hitung yang baru
                            total_jam += aktivitas.durasi
                else:
                    log.delete()
                    error_messages = []
                    for error in aktivitas_formset.errors:
                        error_messages.extend(error.values())
                    messages.error(request, f"Error aktivitas hari {i+1}: {', '.join(error_messages)}")
                    return redirect('LogMahasiswa:create_log')

            log.total_jam = total_jam
            log.save()
            
            messages.success(request, "Log mingguan berhasil disimpan!")
            return redirect('LogMahasiswa:log_detail')
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = LogMingguanForm(program=program)

    return render(request, 'log_form.html', {
        'form': form,
        'program': program
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
    total_jam = logs.aggregate(total=Sum('total_jam'))['total'] or 0.0
    
    return render(request, 'log_detail.html', {
        'program': program,
        'logs': logs,
        'total_jam': total_jam
    })