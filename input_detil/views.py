from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from input_detil.forms import InputDetilKPForm, InputDetilMBKMForm
from input_detil.services import PendaftaranKPService, PendaftaranMBKMService
from database.models import PendaftaranKP, PendaftaranMBKM

# Create your views here.
# class InputDetilKPView(LoginRequiredMixin, UpdateView):
#     model = PendaftaranKP
#     form_class = InputDetilKPForm
#     template_name = 'input_detil/input_detil_kp.html'
#     # success_url = reverse_lazy('input_detil_success')
    
#     def get_object(self):
#         """Dapatkan pendaftaran KP yang masih 'Menunggu Detil' untuk user."""
#         return PendaftaranKPService.get_pending_registration(self.request.user)
    
#     def form_valid(self, form):
#         """Validasi form dan update status pendaftaran jika semua field telah diisi."""
#         registration = form.save()
#         PendaftaranKPService.update_registration_status(registration)
#         return super().form_valid(form)
    
#     def dispatch(self, request, *args, **kwargs):
#         """Pastikan user memiliki pendaftaran yang masih 'Menunggu Detil'."""
#         if not PendaftaranKPService.check_has_pending_registration(request.user):
#             return redirect('input_detil:no_pending_registration')
        
#         return super().dispatch(request, *args, **kwargs)

# @login_required
def input_detil_mbkm(request):
    """
    Function-based view to handle the InputDetilMBKMForm.
    """

    if not PendaftaranMBKMService.check_has_pending_registration(request.user):
        messages.error(request, "You do not have a pending MBKM registration.")
        return redirect('input_detil:no_pending_registration')

    pendaftaran_mbkm = PendaftaranMBKMService.get_pending_registration(request.user)

    if request.method == 'POST':
        form = InputDetilMBKMForm(request.POST, instance=pendaftaran_mbkm)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            return redirect('input_detil:input_detil_mbkm_success', pendaftaran_id=pendaftaran_mbkm.id)
    else:
        form = InputDetilMBKMForm(instance=pendaftaran_mbkm)
    
    return render(request, 'input_detil_mbkm.html', {
        'form': form,
        'pendaftaran_mbkm': pendaftaran_mbkm
    })


# Function-based view untuk menampilkan form input detil KP
@login_required
def input_detil_kp_form(request):
    # if settings.DEBUG:
    #     user, created = User.objects.get_or_create(username='devuser')
    #     login(request, user)

    """Menampilkan form input detil KP dan menangani penyimpanan data."""
    # Cek apakah user memiliki pendaftaran yang masih 'Menunggu Detil'
    if not PendaftaranKPService.check_has_pending_registration(request.user):
        print("masuk sini yeah")
        return redirect('input_detil:no_pending_registration')
    
    # Ambil data pendaftaran KP yang masih 'Menunggu Detil'
    pendaftaran_kp = PendaftaranKPService.get_pending_registration(request.user)
    
    if request.method == 'POST':
        form = InputDetilKPForm(request.POST, instance=pendaftaran_kp)
        if form.is_valid():
            # penyelia_nama = form.cleaned_data.get("penyelia_nama")
            # penyelia_email = form.cleaned_data.get("penyelia_email")
            # penyelia_perusahaan = form.cleaned_data.get("penyelia_perusahaan")

            # Check if a User with the email exists; create one if not
            # user2, created = User.objects.get_or_create(
            #     username=penyelia_email,  # Assuming email as username
            #     defaults={"email": penyelia_email}
            # )

            # # Check if a Penyelia exists for this user; create if not
            # penyelia, created = Penyelia.objects.get_or_create(
            #     user=user2,
            #     defaults={"nama": penyelia_nama, "email": penyelia_email, "perusahaan": penyelia_perusahaan}
            # )

            # Save the form while linking it to the newly created or existing Penyelia
            registration = form.save(commit=False)
            # registration.penyelia = penyelia
            registration.save()
            # PendaftaranKPService.update_registration_status(registration)
            return redirect('input_detil:input_detil_success', pendaftaran_id=pendaftaran_kp.id)
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