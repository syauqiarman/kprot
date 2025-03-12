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
        # Tambahkan field anotasi 'ikut_kp' dan 'ikut_mbkm' untuk filtering
        queryset = queryset.annotate(
            ikut_kp=Exists(PendaftaranKP.objects.filter(mahasiswa=OuterRef("pk"))),
            ikut_mbkm=Exists(PendaftaranMBKM.objects.filter(mahasiswa=OuterRef("pk")))
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
        queryset = queryset.annotate(
        status_kp=Exists(PendaftaranKP.objects.filter(mahasiswa=OuterRef("pk"), status_pendaftaran=value)),
        status_mbkm=Exists(PendaftaranMBKM.objects.filter(mahasiswa=OuterRef("pk"), status_pendaftaran=value))
        )
        return queryset.filter(Q(status_kp=True) | Q(status_mbkm=True))