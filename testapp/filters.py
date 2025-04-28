import django_filters
from testapp.models import *
from django.db.models import *

class MahasiswaFilter(django_filters.FilterSet):
    angkatan = django_filters.CharFilter(field_name='npm', lookup_expr='startswith')
    program = django_filters.CharFilter(method='filter_by_program')
    status = django_filters.CharFilter(method='filter_by_status')
    
    class Meta:
        model = Mahasiswa
        fields = ['angkatan', 'program', 'status']

    def filter_by_program(self, queryset, name, value):
        # Dapatkan semester dari request
        semester_id = self.request.resolver_match.kwargs.get('semester_id')
        if not semester_id:
            # Jika tidak ada semester_id di URL, coba ambil semester aktif
            try:
                semester = Semester.objects.get(aktif=True)
            except Semester.DoesNotExist:
                return queryset
        else:
            try:
                semester = Semester.objects.get(id=semester_id)
            except Semester.DoesNotExist:
                return queryset
                
        # Tambahkan field anotasi 'ikut_kp' dan 'ikut_mbkm' untuk filtering dengan filter semester
        queryset = queryset.annotate(
            ikut_kp=Exists(PendaftaranKP.objects.filter(
                mahasiswa=OuterRef("pk"), 
                semester=semester
            )),
            ikut_mbkm=Exists(PendaftaranMBKM.objects.filter(
                mahasiswa=OuterRef("pk"),
                semester=semester
            ))
        )

        # Lakukan filtering berdasarkan program yang diminta
        if value == "KP":
            return queryset.filter(ikut_kp=True)
        elif value == "MBKM":
            return queryset.filter(ikut_mbkm=True)
        return queryset
    
    def filter_by_status(self, queryset, name, value):
        """
        Filter mahasiswa berdasarkan status pendaftaran KP atau MBKM.
        """
        # Dapatkan semester dari request
        semester_id = self.request.resolver_match.kwargs.get('semester_id')
        if not semester_id:
            # Jika tidak ada semester_id di URL, coba ambil semester aktif
            try:
                semester = Semester.objects.get(aktif=True)
            except Semester.DoesNotExist:
                return queryset
        else:
            try:
                semester = Semester.objects.get(id=semester_id)
            except Semester.DoesNotExist:
                return queryset
        
        # Filter berdasarkan status dan semester tertentu
        queryset = queryset.annotate(
            status_kp=Exists(PendaftaranKP.objects.filter(
                mahasiswa=OuterRef("pk"), 
                status_pendaftaran=value,
                semester=semester
            )),
            status_mbkm=Exists(PendaftaranMBKM.objects.filter(
                mahasiswa=OuterRef("pk"), 
                status_pendaftaran=value,
                semester=semester
            ))
        )
        return queryset.filter(Q(status_kp=True) | Q(status_mbkm=True))