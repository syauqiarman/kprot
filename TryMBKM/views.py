from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import TryMBKMForm
from django.urls import reverse
from PendaftaranMahasiswa.models import PendaftaranMBKM

# Create your views here.
def show_dashboard(request):
    list_daftar = PendaftaranMBKM.objects.all()
    
    context = {
        'list_daftar': list_daftar
    }

    return render(request, "dashboard.html", context)

def daftar_mbkm(request):
    form = PendaftaranMBKM(request.POST or None)

    if form.is_valid() and request.method == "POST":
        form.save()
        return HttpResponseRedirect(reverse('TryMBKM:show_dashboard'))

    context = {'form': form}
    return render(request, "daftar_mbkm.html", context)