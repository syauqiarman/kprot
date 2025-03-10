from django import forms
from django.core.exceptions import ValidationError
from .models import PendaftaranMBKM, ProgramMBKM, Mahasiswa, Semester

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
            'persetujuan_pa', 'tanggal_persetujuan', 'pernyataan_komitmen'
        ]
        labels = {
            'jumlah_semester': 'Jumlah Semester yang Telah Ditempuh',
            'sks_diambil': 'SKS yang Diambil Semester Ini',
            'program_mbkm': 'Program MBKM',
            'estimasi_sks_konversi': 'Estimasi SKS Konversi',
            'rencana_lulus_semester_ini': 'Rencana Lulus Semester Ini',
            'persetujuan_pa': 'Upload Persetujuan PA (PDF)',
            'tanggal_persetujuan': 'Cantumkan Tanggal PA saat Menyetujui Pendaftaran',
            'pernyataan_komitmen': 'Saya menyetujui pernyataan komitmen',
        }
        widgets = {
            'semester': forms.Select(attrs={'class': 'form-control'}),
            'program_mbkm': forms.Select(attrs={'class': 'form-control'}),
            'persetujuan_pa': forms.ClearableFileInput(attrs={'accept': 'application/pdf'}),
            'tanggal_persetujuan': forms.DateInput(attrs={'type': 'date'}),
            'pernyataan_komitmen': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Ambil data mahasiswa dari user yang sedang login
        if self.user and hasattr(self.user, 'mahasiswa'):
            mahasiswa = self.user.mahasiswa
            self.fields['nama'].initial = mahasiswa.nama
            self.fields['npm'].initial = mahasiswa.npm
            self.fields['email'].initial = mahasiswa.email
        
        # Konfigurasi pilihan program MBKM
        self.fields['program_mbkm'].queryset = ProgramMBKM.objects.all()
        self.fields['program_mbkm'].empty_label = "Pilih Program MBKM"  # Tambahkan placeholder

        # Konfigurasi pilihan semester
        self.fields['semester'].queryset = Semester.objects.all()
        self.fields['semester'].empty_label = "Pilih Semester"  # Tambahkan placeholder

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
        pernyataan_komitmen = cleaned_data.get('pernyataan_komitmen')
        persetujuan_pa = cleaned_data.get('persetujuan_pa')
        tanggal_persetujuan = cleaned_data.get('tanggal_persetujuan')

        # Validasi: Jika ada file persetujuan PA, tanggal_persetujuan harus diisi
        if persetujuan_pa and not tanggal_persetujuan:
            raise ValidationError({
                'tanggal_persetujuan': "Tanggal persetujuan harus diisi jika file persetujuan PA diupload."
            })

        # Validasi pernyataan komitmen
        if not pernyataan_komitmen:
            raise ValidationError({
                'pernyataan_komitmen': "Anda harus menyetujui pernyataan komitmen."
            })
        
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