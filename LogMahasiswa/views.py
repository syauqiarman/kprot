from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from database.models import AktivitasHarian, LogMingguan, PendaftaranKP, PendaftaranMBKM
from django.db.models import Sum
from LogMahasiswa.forms import AktivitasHarianForm, LogMingguanForm, AktivitasHarianFormSet
from django.db.models import Prefetch

def create_log(request):
    """View utama untuk membuat log aktivitas."""
    program = _get_active_program(request)
    if not program:
        messages.warning(request, "Anda belum memiliki program yang aktif")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if request.method == 'POST':
        return _handle_post_request(request, program)
    return _render_form(request, program)

def _get_active_program(request):
    """Mengambil program aktif (KP atau MBKM) untuk mahasiswa."""
    try:
        return PendaftaranKP.objects.get(
            mahasiswa__user=request.user,
            status_pendaftaran='Terdaftar',
            semester__aktif=True
        )
    except PendaftaranKP.DoesNotExist:
        try:
            return PendaftaranMBKM.objects.get(
                mahasiswa__user=request.user,
                status_pendaftaran='Terdaftar',
                semester__aktif=True
            )
        except PendaftaranMBKM.DoesNotExist:
            return None

def _handle_post_request(request, program):
    """Menangani request POST untuk pembuatan log."""
    form = LogMingguanForm(request.POST, program=program)
    dates = _process_dates(request.POST)
    
    # Hitung jumlah form yang aktif (tidak dihapus)
    total_forms = int(request.POST.get('aktivitas_harian-TOTAL_FORMS', 0))
    active_forms = 0
    for i in range(total_forms):
        if not request.POST.get(f'aktivitas_harian-{i}-DELETE'):
            active_forms += 1
    
    # Validasi minimal satu aktivitas
    if active_forms == 0:
        messages.error(request, "Minimal harus ada satu aktivitas harian")
        return _render_form(request, program)
    
    if form.is_valid():
        return _handle_valid_form(request, form, program)
    
    return _handle_invalid_form(request, form, program, dates)

def _process_dates(post_data):
    """Memproses dan memvalidasi tanggal dari POST data."""
    tanggal_mulai_str = post_data.get('tanggal_mulai')
    tanggal_selesai_str = post_data.get('tanggal_selesai')
    dates = []

    if tanggal_mulai_str and tanggal_selesai_str:
        try:
            start_date = datetime.strptime(tanggal_mulai_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(tanggal_selesai_str, "%Y-%m-%d").date()
            dates = [start_date + timedelta(days=i) 
                    for i in range((end_date - start_date).days + 1)]
        except ValueError:
            pass

    return dates

def _handle_valid_form(request, form, program):
    """Menangani form yang valid dan menyimpan log."""
    log = _save_log(form, program)
    formset = AktivitasHarianFormSet(request.POST, instance=log)
    
    if formset.is_valid():
        return _save_valid_formset(request, formset, log)
    
    return _handle_invalid_formset(request, formset, log)

def _save_log(form, program):
    """Menyimpan log mingguan ke database."""
    log = form.save(commit=False)
    if isinstance(program, PendaftaranKP):
        log.pendaftaran_kp = program
    else:
        log.pendaftaran_mbkm = program
    log.save()
    return log

def _save_valid_formset(request, formset, log):
    """Menyimpan formset yang valid dan mengupdate total jam."""
    formset.save()
    log.total_jam = log.calculate_total_jam()
    log.save()
    
    if _is_ajax_request(request):
        return JsonResponse({
            'success': True,
            'redirect_url': reverse('LogMahasiswa:log_detail')
        })
    
    messages.success(request, "Log mingguan berhasil disimpan!")
    return redirect('LogMahasiswa:log_detail')

def _handle_invalid_formset(request, formset, log):
    """Menangani formset yang tidak valid."""
    log.delete()
    if _is_ajax_request(request):
        return JsonResponse({
            'success': False,
            'formset_errors': [f.errors for f in formset]
        })
    
    messages.error(request, "Terjadi kesalahan pada aktivitas harian")
    return _render_form(request, log.program)

def _handle_invalid_form(request, form, program, dates):
    """Menangani form yang tidak valid."""
    for error in form.non_field_errors():
        messages.error(request, error)
    
    formset = AktivitasHarianFormSet(request.POST)
    if _is_ajax_request(request):
        return JsonResponse({
            'success': False,
            'form_errors': form.errors,
            'formset_errors': [f.errors for f in formset],
            'non_field_errors': form.non_field_errors()
        })
    
    return _render_form(request, program, form, formset, dates)

def _render_form(request, program, form=None, formset=None, dates=None):
    """Merender form log mingguan."""
    context = {
        'form': form or LogMingguanForm(program=program),
        'formset': formset or AktivitasHarianFormSet(),
        'program': program,
        'zipped_data': zip(formset or [], dates or [])
    }
    return render(request, 'log_form.html', context)

def _is_ajax_request(request):
    """Mengecek apakah request adalah AJAX request."""
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'

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
        logs = LogMingguan.objects.filter(pendaftaran_kp=program).order_by('-tanggal_mulai').prefetch_related(
            Prefetch(
                'aktivitas_harian',
                queryset=AktivitasHarian.objects.order_by('tanggal', 'jam_mulai')
            )
        )
    else:
        logs = LogMingguan.objects.filter(pendaftaran_mbkm=program).order_by('-tanggal_mulai').prefetch_related(
            Prefetch(
                'aktivitas_harian',
                queryset=AktivitasHarian.objects.order_by('tanggal', 'jam_mulai')
            )
        )
    
    if not logs.exists():
        messages.info(request, "Belum ada log mingguan yang tercatat.")

    # Hitung total jam dari semua log
    total_jam = logs.aggregate(total=Sum('total_jam'))['total'] or 0.0
    
    return render(request, 'log_detail.html', {
        'program': program,
        'logs': logs,
        'total_jam': total_jam
    })