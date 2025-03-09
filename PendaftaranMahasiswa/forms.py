from django import forms
from django.core.exceptions import ValidationError
from .models import PendaftaranMBKM, ProgramMBKM, Mahasiswa

class PendaftaranMBKMForm(forms.ModelForm):
    nama = forms.CharField(disabled=True, required=False, label="Nama Mahasiswa")
    npm = forms.CharField(disabled=True, required=False, label="NPM")
    email = forms.EmailField(disabled=True, required=False, label="Email Mahasiswa")

    class Meta:
        model = PendaftaranMBKM
        fields = [
            'nama', 'npm', 'email',
            'semester', 'jumlah_semester', 'sks_diambil', 'program_mbkm',
            'estimasi_sks_konversi', 'rencana_lulus_semester_ini',
            'persetujuan_pa'
        ]
        labels = {
            'jumlah_semester': 'Jumlah Semester yang Telah Ditempuh',
            'sks_diambil': 'SKS yang Diambil Semester Ini',
            'program_mbkm': 'Program MBKM',
            'estimasi_sks_konversi': 'Estimasi SKS Konversi',
            'rencana_lulus_semester_ini': 'Rencana Lulus Semester Ini',
            'persetujuan_pa': 'Upload Persetujuan PA (PDF)'
        }
        widgets = {
            'persetujuan_pa': forms.ClearableFileInput(attrs={'accept': 'application/pdf'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and hasattr(user, 'mahasiswa'):
            mahasiswa = user.mahasiswa
            self.fields['nama'].initial = mahasiswa.nama
            self.fields['npm'].initial = mahasiswa.npm
            self.fields['email'].initial = mahasiswa.email
        
        self.fields['program_mbkm'].queryset = ProgramMBKM.objects.all()
        self.fields['program_mbkm'].empty_label = None

    def clean_persetujuan_pa(self):
        file = self.cleaned_data.get('persetujuan_pa')
        if file and file.content_type != 'application/pdf':
            raise ValidationError("File harus dalam format PDF.")
        return file

    def clean(self):
        cleaned_data = super().clean()
        jumlah_semester = cleaned_data.get('jumlah_semester')
        sks_diambil = cleaned_data.get('sks_diambil', 0)
        estimasi_sks_konversi = cleaned_data.get('estimasi_sks_konversi', 0)
        program_mbkm = cleaned_data.get('program_mbkm')

        # Validasi jumlah semester
        if jumlah_semester and jumlah_semester < 5:
            raise ValidationError({
                'jumlah_semester': "Minimal 5 semester untuk mendaftar program MBKM."
            })

        # Validasi program MBKM harus dipilih
        if not program_mbkm:
            raise ValidationError({
                'program_mbkm': "Program MBKM harus dipilih."
            })

        # Validasi estimasi SKS konversi
        if estimasi_sks_konversi is not None:
            if not (program_mbkm.minimum_sks <= estimasi_sks_konversi <= program_mbkm.maksimum_sks):
                raise ValidationError({
                    'estimasi_sks_konversi': f"Estimasi SKS konversi untuk program {program_mbkm.nama} harus antara {program_mbkm.minimum_sks} dan {program_mbkm.maksimum_sks}."
                })

            # Validasi total SKS
            if sks_diambil + estimasi_sks_konversi > 24:
                raise ValidationError({
                    'estimasi_sks_konversi': "Total SKS (sks_diambil + estimasi_sks_konversi) tidak boleh lebih dari 24."
                })

        return cleaned_data