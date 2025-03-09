from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from .models import PendaftaranKP, Mahasiswa, Semester
from .forms import PendaftaranKPForm

class InputDetilKPView(LoginRequiredMixin, CreateView):
    model = PendaftaranKP
    form_class = PendaftaranKPForm
    template_name = 'input_detil_program/input_detil_kp.html'
    success_url = reverse_lazy('success_page')

    def get_form_kwargs(self):
        """Tambahkan mahasiswa dan semester ke dalam form"""
        kwargs = super().get_form_kwargs()
        mahasiswa = Mahasiswa.objects.get(user=self.request.user)
        semester = Semester.objects.latest('id')  # Ambil semester terbaru
        kwargs.update({'mahasiswa': mahasiswa, 'semester': semester})
        return kwargs

    def form_valid(self, form):
        """Set status pendaftaran dan simpan form"""
        form.instance.status_pendaftaran = "Menunggu Detil"
        return super().form_valid(form)
