from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from database.models import LogMingguan, PendaftaranKP, PendaftaranMBKM
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
            return redirect('create-log')

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
                return redirect('log-detail', log_id=log.id)
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

def log_detail(request, log_id):
    log = get_object_or_404(LogMingguan, pk=log_id)
    context = {
        'log': log
    }
    return render(request, 'log_detail.html', context)