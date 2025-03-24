from django import forms
from django.core.exceptions import ValidationError
from database.models import PendaftaranMBKM, ProgramMBKM, Mahasiswa, Semester

class PendaftaranMBKMForm(forms.ModelForm):
    nama = forms.CharField(disabled=True, required=False, label="Nama Mahasiswa")
    npm = forms.CharField(disabled=True, required=False, label="NPM")
    email = forms.EmailField(disabled=True, required=False, label="Email Mahasiswa")
    prodi = forms.CharField(disabled=True, required=False, label="Program Studi")

    class Meta:
        model = PendaftaranMBKM
        fields = [
            'nama', 'npm', 'email', 'prodi',
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
            'persetujuan_pa': 'Upload PDF Persetujuan PA (Opsional)',
            'tanggal_persetujuan': 'Tanggal PA saat Menyetujui Pendaftaran (Opsional)',
            'pernyataan_komitmen': 'Saya menyatakan bahwa semua informasi yang diberikan benar dan bersedia mengikuti program hingga selesai',
        }
        widgets = {
            'program_mbkm': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent'
            }),
            'sks_diambil': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent',
                'min': 0
            }),
            'estimasi_sks_konversi': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent',
                'min': 1
            }),
            'jumlah_semester': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent',
                'min': 1
            }),
            'tanggal_persetujuan': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent'
            }),
            'pernyataan_komitmen': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-gray-600 border-gray-300 rounded focus:ring-gray-500'
            }),

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
            self.fields['prodi'].initial = mahasiswa.prodi
            
        # Set nilai default untuk semester (semester yang aktif)
        semester_aktif = Semester.objects.filter(aktif=True).first()
        if semester_aktif:
            self.fields['semester'].initial = semester_aktif
            self.fields['semester'].disabled = True  # Nonaktifkan field

        # Konfigurasi pilihan program MBKM
        self.fields['program_mbkm'].queryset = ProgramMBKM.objects.all()
        self.fields['program_mbkm'].empty_label = "Pilih Program MBKM"  # Tambahkan placeholder

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
        mahasiswa = self.user.mahasiswa
        semester = cleaned_data.get('semester')

        if PendaftaranMBKM.objects.filter(mahasiswa=mahasiswa, semester=semester).exists():
            raise ValidationError("Anda sudah mendaftar di semester ini.")
        
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
    
    def save(self, commit=True):
        # Ambil instance PendaftaranMBKM
        pendaftaran = super().save(commit=False)
        pendaftaran.mahasiswa = self.user.mahasiswa
        
        # Atur status pendaftaran berdasarkan ada/tidaknya file persetujuan PA
        if pendaftaran.persetujuan_pa:
            pendaftaran.status_pendaftaran = "Menunggu Verifikasi Dosen"
        else:
            pendaftaran.status_pendaftaran = "Menunggu Persetujuan PA"
        
        # Simpan ke database jika commit=True
        if commit:
            pendaftaran.save()
        
        return pendaftaran