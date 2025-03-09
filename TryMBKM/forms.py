from django.forms import ModelForm
from PendaftaranMahasiswa.models import PendaftaranMBKM

class TryMBKMForm(ModelForm):
    class Meta:
        model = PendaftaranMBKM
        fields = ['mahasiswa', 'semester', 'jumlah_semester', 'sks_diambil', 'program_mbkm',
                'estimasi_sks_konversi', 'tanggal_persetujuan', 'persetujuan_pa',
                'request_status_merdeka', 'rencana_lulus_semester_ini', 'pernyataan_komitmen']