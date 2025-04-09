from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from database.models import AktivitasHarian, LogMingguan, PendaftaranKP, PendaftaranMBKM
from django.db.models import Sum
from LogMahasiswa.forms import AktivitasHarianForm, LogMingguanForm, AktivitasHarianFormSet

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
        post_data = request.POST.copy()
        tanggal_mulai_str = post_data.get('tanggal_mulai')
        tanggal_selesai_str = post_data.get('tanggal_selesai')
        dates = []
        num_days = 7  # Default 7 hari jika tidak ada tanggal

        if tanggal_mulai_str and tanggal_selesai_str:
            try:
                start_date = datetime.strptime(tanggal_mulai_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(tanggal_selesai_str, "%Y-%m-%d").date()
                num_days = (end_date - start_date).days + 1
                dates = [start_date + timedelta(days=i) for i in range(num_days)]
            except:
                pass  # Tetap gunakan default jika parsing gagal

        # Sesuaikan data POST untuk formset
        post_data['aktivitas_harian-TOTAL_FORMS'] = num_days
        form = LogMingguanForm(post_data, program=program)
        
        if form.is_valid():
            # Simpan log terlebih dahulu
            log = form.save(commit=False)
            if isinstance(program, PendaftaranKP):
                log.pendaftaran_kp = program
            else:
                log.pendaftaran_mbkm = program
            log.save()  # Simpan untuk mendapatkan ID
            
            # Sekarang proses formset dengan instance yang sudah ada
            formset = AktivitasHarianFormSet(post_data, instance=log)
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
            for error in form.non_field_errors():
                messages.error(request, error)
            formset = AktivitasHarianFormSet(post_data)
    else:
        form = LogMingguanForm(program=program)
        formset = AktivitasHarianFormSet()

    return render(request, 'log_form.html', {
        'form': form,
        'formset': formset,
        'program': program,
        'zipped_data': zip(formset, dates if request.method == 'POST' else [])
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