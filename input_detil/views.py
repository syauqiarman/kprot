from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import InputDetilKPForm
from .services import PendaftaranKPService
from .models import PendaftaranKP, Semester
from django.views.decorators.http import require_GET, require_POST

# Function-based view untuk menampilkan form input detil KP
@login_required
@require_GET
def input_detil_kp_form(request):
    mahasiswa = request.user.mahasiswa
    semester_aktif = Semester.objects.filter(aktif=True).first()

    # Ambil data pendaftaran yang sudah ada
    existing_pendaftaran = PendaftaranKP.objects.filter(
        mahasiswa=mahasiswa, 
        semester=semester_aktif
    ).first()

    """Menampilkan form input detil KP dan menangani penyimpanan data."""
    # Cek apakah user memiliki pendaftaran yang masih 'Menunggu Detil'
    if not PendaftaranKPService.check_has_pending_registration(existing_pendaftaran):
        return redirect('input_detil:no_pending_registration')

    pendaftaran_kp = PendaftaranKPService.get_pending_registration(request.user)
    form = InputDetilKPForm(instance=pendaftaran_kp)
    
    return render(request, 'input_detil_kp.html', {
        'form': form,
        'pendaftaran': pendaftaran_kp
    })

@login_required
@require_POST
def simpan_detil_kp(request, pendaftaran_id):
    if request.method != 'POST':
        return redirect('input_detil:input_detil_kp')

    mahasiswa = request.user.mahasiswa
    semester_aktif = Semester.objects.filter(aktif=True).first()

    existing_pendaftaran = PendaftaranKP.objects.filter(
        mahasiswa=mahasiswa,
        semester=semester_aktif
    ).first()

    if not PendaftaranKPService.check_has_pending_registration(existing_pendaftaran):
        return redirect('input_detil:no_pending_registration')

    pendaftaran_kp = PendaftaranKPService.get_pending_registration(request.user)
    form = InputDetilKPForm(request.POST, instance=pendaftaran_kp)

    if form.is_valid():
        registration = form.save(commit=False)
        registration.save()
        return redirect('input_detil:input_detil_success', pendaftaran_id=pendaftaran_kp.id)

    return render(request, 'input_detil_kp.html', {
        'form': form,
        'pendaftaran': pendaftaran_kp
    })

@login_required
@require_GET
def no_pending_registration(request):
    return render(request, 'no_pending.html')

@login_required
@require_GET
def input_detil_success(request, pendaftaran_id):
    pendaftaran = PendaftaranKP.objects.get(id=pendaftaran_id)
    return render(request, 'success_page.html', {'pendaftaran': pendaftaran})

