from django import forms
from .models import PendaftaranMBKM, ProgramMBKM
from datetime import timedelta, date

class PendaftaranMBKMForm(forms.ModelForm):
    PROGRAM_CHOICES = [
        ("Magang Mandiri", 20),
        ("Studi Independen", 20),
        ("Magang BUMN", 10),  # Min 10, Max 20 (akan dikontrol di validasi)
        ("Magang Mitra", 20),
        ("Apple Academy", 10),
        ("Kewirausahaan", 10),
    ]

    # Add readonly display fields (not part of model save)
    mahasiswa = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), required=False)
    npm = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), required=False)
    semester = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), required=False)
    jumlah_semester = forms.IntegerField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), required=False)
    sks_diambil = forms.IntegerField(widget=forms.NumberInput(attrs={'readonly': 'readonly'}), required=False)
    program_mbkm = forms.ModelMultipleChoiceField(
        queryset=ProgramMBKM.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Program MBKM"
    )
    estimasi_sks_konversi = forms.IntegerField(required=True)
    request_status_merdeka = forms.BooleanField(required=False)
    rencana_lulus_semester_ini = forms.BooleanField(required=False)
    pernyataan_komitmen = forms.BooleanField(required=True)

    persetujuan_pa = forms.FileField(required=False, label="Upload Persetujuan PA (Opsional, PDF)")
    tanggal_persetujuan = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    class Meta:
        model = PendaftaranMBKM
        fields = [
            'mahasiswa', 'npm', 'semester', 'jumlah_semester', 'sks_diambil', 'program_mbkm',
            'estimasi_sks_konversi', 'tanggal_persetujuan', 'persetujuan_pa',
            'request_status_merdeka', 'rencana_lulus_semester_ini', 'pernyataan_komitmen'
        ]

    def __init__(self, *args, **kwargs):
        # Get the pendaftaran_mbkm instance 
        self.pendaftaran_mbkm = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        
        if self.pendaftaran_mbkm:
            # Pre-fill the readonly fields
            self.fields['mahasiswa'].initial = getattr(self.pendaftaran_mbkm.mahasiswa, "nama", "")
            self.fields['npm'].initial = getattr(self.pendaftaran_mbkm.mahasiswa, "npm", "")
            self.fields['semester'].initial = getattr(self.pendaftaran_mbkm.semester.nama, "semester", "")
            self.fields['sks_diambil'].initial = getattr(self.pendaftaran_mbkm, "sks_diambil", 0)

        if int(self.fields['jumlah_semester'].initial) < 5:
            self.fields['program_mbkm'].widget.attrs['disabled'] = 'disabled'

    def clean_estimasi_sks_konversi(self):
        program_mbkm = self.cleaned_data.get("program_mbkm", [])
        sks_max = {
            "Magang Mandiri": 20,
            "Studi Independen": 20,
            "Magang BUMN": 20,
            "Magang Mitra": 20,
            "Apple Academy": 10,
            "Kewirausahaan": 10,
        }
        
        total_sks = sum(sks_max.get(p, 0) for p in program_mbkm)
        estimasi_sks = self.cleaned_data.get("estimasi_sks_konversi")
        
        if estimasi_sks > total_sks:
            raise forms.ValidationError(f"Maksimal SKS yang bisa dikonversi adalah {total_sks} berdasarkan program yang dipilih.")
        return estimasi_sks
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if instance.jumlah_semester < 5:
            return instance  # Tidak menyimpan jika semester kurang dari 5
        
        if self.cleaned_data.get("persetujuan_pa"):
            instance.status_pendaftaran = "Menunggu Verifikasi Dosen"
        else:
            instance.status_pendaftaran = "Menunggu Persetujuan PA"
        
        if commit:
            instance.save()
        return instance

    # def clean_jumlah_semester(self):
    #     jumlah_semester = self.cleaned_data.get('jumlah_semester')
    #     if jumlah_semester < 5:
    #         raise forms.ValidationError("Mahasiswa harus berada di semester 5 atau lebih untuk mendaftar.")
    #     return jumlah_semester

    # def clean_sks_diambil(self):
    #     sks_diambil = self.cleaned_data.get('sks_diambil')
    #     program = self.cleaned_data.get('program_mbkm')
        
    #     if program and (sks_diambil < program.minimum_sks or sks_diambil > program.maksimum_sks):
    #         raise forms.ValidationError(f"Jumlah SKS harus antara {program.minimum_sks} dan {program.maksimum_sks}.")
        
    #     return sks_diambil

    # def clean_estimasi_sks_konversi(self):
    #     estimasi_sks = self.cleaned_data.get("estimasi_sks_konversi")
    #     jenis_magang = self.cleaned_data.get("jenis_magang")

    #     # Debugging untuk melihat nilai saat validasi berjalan
    #     # print(f"Debug Validasi SKS: {estimasi_sks}, Jenis Magang: {jenis_magang}")

    #     # Pastikan field tidak kosong atau None
    #     if estimasi_sks is None:
    #         raise forms.ValidationError("Estimasi SKS konversi harus diisi.")

    #     # Validasi batas maksimum dan minimum SKS konversi
    #     if estimasi_sks > 20 or estimasi_sks <= 0:
    #         # print("Validasi Gagal: SKS melebihi batas!")  # Debugging
    #         raise forms.ValidationError("Estimasi SKS konversi tidak boleh lebih dari 20 SKS atau 0 dan Angka negatif.")

    #     # Validasi khusus jika program adalah Studi Independen
    #     if jenis_magang and "studi_independent" in jenis_magang and estimasi_sks > 10:
    #         # print("Validasi Gagal: SKS Studi Independen melebihi batas 10 SKS!")  # Debugging
    #         raise forms.ValidationError("Estimasi SKS konversi untuk Studi Independen tidak boleh lebih dari 10 SKS.")

    #     return estimasi_sks


    # def clean_pernyataan_komitmen(self):
    #     pernyataan_komitmen = self.cleaned_data.get('pernyataan_komitmen')
    #     if not pernyataan_komitmen:
    #         raise forms.ValidationError("Anda harus menyetujui pernyataan komitmen untuk melanjutkan pendaftaran.")
    #     return pernyataan_komitmen

    # def clean_tanggal_mulai(self):
    #     tanggal_mulai = self.cleaned_data.get('tanggal_mulai')

    #     if tanggal_mulai and tanggal_mulai < date.today():
    #         raise forms.ValidationError("Tanggal mulai tidak boleh di masa lalu.")

    #     return tanggal_mulai

    # def clean(self):
    #     cleaned_data = super().clean()
    #     tanggal_mulai = cleaned_data.get('tanggal_mulai')

    #     if tanggal_mulai:
    #         cleaned_data['tanggal_selesai'] = tanggal_mulai + timedelta(days=5*30)  # Tambah 5 bulan

    #     return cleaned_data