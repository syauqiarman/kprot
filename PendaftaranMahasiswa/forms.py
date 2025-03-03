from django import forms
from .models import PendaftaranMBKM, ProgramMBKM
from datetime import timedelta, date

# Opsi Jenis Magang
JENIS_MAGANG_CHOICES = [
    ('studi_independent', 'Studi Independent (Maks 10 SKS)'),
    ('magang_mandiri', 'Magang Mandiri (Maks 20 SKS)'),
    ('magang_mitra', 'Magang Mitra (Maks 20 SKS)'),
]

class PendaftaranMBKMForm(forms.ModelForm):
    jenis_magang = forms.MultipleChoiceField(
        choices=JENIS_MAGANG_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Pilih Jenis Magang"
    )
    
    persetujuan_pa = forms.FileField(
        required=False,
        label="Upload Persetujuan PA (Opsional, PDF)",
        widget=forms.ClearableFileInput(attrs={'accept': 'application/pdf'})
    )

    class Meta:
        model = PendaftaranMBKM
        fields = [
            'mahasiswa', 'semester', 'jumlah_semester', 'sks_diambil', 
            'program_mbkm', 'penyelia', 'role', 'estimasi_sks_konversi', 
            'tanggal_mulai', 'pernyataan_komitmen', 'status_pendaftaran',
            'persetujuan_pa', 'jenis_magang'
        ]

    def clean_jumlah_semester(self):
        jumlah_semester = self.cleaned_data.get('jumlah_semester')
        if jumlah_semester < 5:
            raise forms.ValidationError("Mahasiswa harus berada di semester 5 atau lebih untuk mendaftar.")
        return jumlah_semester

    def clean_sks_diambil(self):
        sks_diambil = self.cleaned_data.get('sks_diambil')
        program = self.cleaned_data.get('program_mbkm')
        
        if program and (sks_diambil < program.minimum_sks or sks_diambil > program.maksimum_sks):
            raise forms.ValidationError(f"Jumlah SKS harus antara {program.minimum_sks} dan {program.maksimum_sks}.")
        
        return sks_diambil

    def clean_estimasi_sks_konversi(self):
        estimasi_sks = self.cleaned_data.get("estimasi_sks_konversi")
        jenis_magang = self.cleaned_data.get("jenis_magang")

        # Debugging untuk melihat nilai saat validasi berjalan
        # print(f"Debug Validasi SKS: {estimasi_sks}, Jenis Magang: {jenis_magang}")

        # Pastikan field tidak kosong atau None
        if estimasi_sks is None:
            raise forms.ValidationError("Estimasi SKS konversi harus diisi.")

        # Validasi batas maksimum dan minimum SKS konversi
        if estimasi_sks > 20 or estimasi_sks <= 0:
            # print("Validasi Gagal: SKS melebihi batas!")  # Debugging
            raise forms.ValidationError("Estimasi SKS konversi tidak boleh lebih dari 20 SKS atau 0 dan Angka negatif.")

        # Validasi khusus jika program adalah Studi Independen
        if jenis_magang and "studi_independent" in jenis_magang and estimasi_sks > 10:
            # print("Validasi Gagal: SKS Studi Independen melebihi batas 10 SKS!")  # Debugging
            raise forms.ValidationError("Estimasi SKS konversi untuk Studi Independen tidak boleh lebih dari 10 SKS.")

        return estimasi_sks


    def clean_pernyataan_komitmen(self):
        pernyataan_komitmen = self.cleaned_data.get('pernyataan_komitmen')
        if not pernyataan_komitmen:
            raise forms.ValidationError("Anda harus menyetujui pernyataan komitmen untuk melanjutkan pendaftaran.")
        return pernyataan_komitmen

    def clean_tanggal_mulai(self):
        tanggal_mulai = self.cleaned_data.get('tanggal_mulai')

        if tanggal_mulai and tanggal_mulai < date.today():
            raise forms.ValidationError("Tanggal mulai tidak boleh di masa lalu.")

        return tanggal_mulai

    def clean(self):
        cleaned_data = super().clean()
        tanggal_mulai = cleaned_data.get('tanggal_mulai')

        if tanggal_mulai:
            cleaned_data['tanggal_selesai'] = tanggal_mulai + timedelta(days=5*30)  # Tambah 5 bulan

        return cleaned_data
