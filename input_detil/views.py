from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from input_detil.forms import InputDetilKPForm, InputDetilMBKMForm
from input_detil.services import PendaftaranKPService, PendaftaranMBKMService
from database.models import PendaftaranKP, PendaftaranMBKM

@login_required
def input_detil_mbkm(request):
    """
    Function-based view to handle the InputDetilMBKMForm.
    """     
    if not PendaftaranMBKMService.check_has_pending_registration(request.user):
        messages.error(request, "You do not have a pending MBKM registration.")
        return redirect('input_detil_program:no_pending_registration')

    pendaftaran_mbkm = PendaftaranMBKMService.get_pending_registration(request.user)

    if request.method == 'POST':
        form = InputDetilMBKMForm(request.POST, instance=pendaftaran_mbkm)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            return redirect('input_detil_program:input_detil_mbkm_success', pendaftaran_id=pendaftaran_mbkm.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = InputDetilMBKMForm(instance=pendaftaran_mbkm)
    
    return render(request, 'input_detil_mbkm.html', {
        'form': form,
        'pendaftaran_mbkm': pendaftaran_mbkm
    })

@login_required
def input_detil_kp_form(request):
    """Menampilkan form input detil KP dan menangani penyimpanan data."""
    # Cek apakah user memiliki pendaftaran yang masih 'Menunggu Detil'
    if not PendaftaranKPService.check_has_pending_registration(request.user):
        return redirect('input_detil_program:no_pending_registration')
    
    # Ambil data pendaftaran KP yang masih 'Menunggu Detil'
    pendaftaran_kp = PendaftaranKPService.get_pending_registration(request.user)
    
    if request.method == 'POST':
        form = InputDetilKPForm(request.POST, instance=pendaftaran_kp)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.save()
            return redirect('input_detil_program:input_detil_success', pendaftaran_id=pendaftaran_kp.id)
    else:
        form = InputDetilKPForm(instance=pendaftaran_kp)
    
    return render(request, 'input_detil_kp.html', {
        'form': form,
        'pendaftaran': pendaftaran_kp
    })

@login_required
def no_pending_registration(request):
    return render(request, 'no_pending.html')

@login_required
def input_detil_success(request, pendaftaran_id):
    pendaftaran = PendaftaranKP.objects.get(id=pendaftaran_id)
    return render(request, 'success_page.html', {'pendaftaran': pendaftaran})

@login_required
def input_detil_mbkm_success(request, pendaftaran_id):
    pendaftaran = PendaftaranMBKM.objects.get(id=pendaftaran_id)
    return render(request, 'mbkm_success_page.html', {'pendaftaran': pendaftaran})