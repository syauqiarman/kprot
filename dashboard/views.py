# dashboard/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from database.models import Semester  # Import model Semester dari testapp

@login_required
def dashboard(request):
    semesters = Semester.objects.all().order_by('-tahun', '-gasal_genap')  # Ambil semua semester
    return render(request, 'dashboard.html', {'semesters': semesters})