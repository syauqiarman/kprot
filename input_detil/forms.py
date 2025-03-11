from django import forms
from .models import PendaftaranKP, Penyelia, Semester, User
import secrets

class InputDetilKPForm(forms.ModelForm):
    class Meta:
        model = PendaftaranKP
        fields = ['role', 'total_jam_kerja', 'tanggal_mulai', 'tanggal_selesai']
        widgets = {
            'tanggal_mulai': forms.DateInput(attrs={'type': 'date'}),
            'tanggal_selesai': forms.DateInput(attrs={'type': 'date'}),
        }

    # Readonly fields (tidak akan disimpan ke model)
    mahasiswa = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), required=False)
    npm = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), required=False)
    semester = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), required=False)
    sks_lulus = forms.IntegerField(widget=forms.NumberInput(attrs={'readonly': 'readonly'}), required=False)

    # Penyelia fields (tidak termasuk dalam model secara langsung)
    penyelia_nama = forms.CharField(required=False, label="Nama Penyelia")
    penyelia_perusahaan = forms.CharField(required=False, label="Perusahaan Penyelia")
    penyelia_email = forms.EmailField(required=False, label="Email Penyelia")

    def __init__(self, *args, **kwargs):
        """Inisialisasi form dengan data yang sudah ada dari model"""
        self.pendaftaran_kp = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        if self.pendaftaran_kp:
            # Prefill readonly fields dari instance mahasiswa
            self.fields['mahasiswa'].initial = getattr(self.pendaftaran_kp.mahasiswa, "nama", "")
            self.fields['npm'].initial = getattr(self.pendaftaran_kp.mahasiswa, "npm", "")
            self.fields['semester'].initial = getattr(self.pendaftaran_kp.semester, "nama", "")
            self.fields['sks_lulus'].initial = getattr(self.pendaftaran_kp, "sks_lulus", 0)

            # Jika ada penyelia, prefill data
            if self.pendaftaran_kp.penyelia:
                self.fields['penyelia_nama'].initial = self.pendaftaran_kp.penyelia.nama
                self.fields['penyelia_perusahaan'].initial = self.pendaftaran_kp.penyelia.perusahaan
                self.fields['penyelia_email'].initial = self.pendaftaran_kp.penyelia.email

    def clean(self):
        cleaned_data = super().clean()

        # Hapus field readonly agar tidak masuk ke cleaned_data
        readonly_fields = ["mahasiswa", "npm", "semester", "sks_lulus"]
        for field in readonly_fields:
            cleaned_data.pop(field, None)  # Hapus jika ada
            
        # Validasi kelengkapan sebelum status bisa menjadi "Terdaftar"
        required_fields = ["role", "total_jam_kerja", "penyelia_nama", "penyelia_perusahaan", "penyelia_email", "tanggal_mulai", "tanggal_selesai"]
        errors = {}

        for field in required_fields:
            if not cleaned_data.get(field):
                errors[field] = f"{self.fields[field].label} harus diisi sebelum status bisa menjadi Terdaftar."

        if errors:
            raise forms.ValidationError(errors)
        
        tanggal_mulai = cleaned_data.get("tanggal_mulai")
        tanggal_selesai = cleaned_data.get("tanggal_selesai")

        if tanggal_mulai and tanggal_selesai and tanggal_mulai > tanggal_selesai:
            raise forms.ValidationError({"__all__": "Tanggal selesai harus setelah tanggal mulai."})

        return cleaned_data

    def save(self, commit=True):
        """Simpan form dan perbarui status_pendaftaran secara otomatis"""
        instance = super().save(commit=False)

        # Cek apakah semua field sudah terisi, lalu ubah status_pendaftaran
        required_fields = ["role", "total_jam_kerja", "penyelia_nama", "penyelia_perusahaan", "penyelia_email", "tanggal_mulai", "tanggal_selesai"]
        is_complete = all(self.cleaned_data.get(field) for field in required_fields)

        instance.status_pendaftaran = "Terdaftar" if is_complete else "Menunggu Detil"

        # Update atau buat penyelia
        penyelia_nama = self.cleaned_data.get("penyelia_nama")
        penyelia_perusahaan = self.cleaned_data.get("penyelia_perusahaan")
        penyelia_email = self.cleaned_data.get("penyelia_email")

        # Check if a User with the email exists; create one if not
        user2, created = User.objects.get_or_create(
            username=penyelia_email,  # Assuming email as username
            defaults={"email": penyelia_email}
        )

        if penyelia_nama and penyelia_perusahaan and penyelia_email:
            penyelia, created = Penyelia.objects.get_or_create(
                nama=penyelia_nama,
                defaults={"perusahaan": penyelia_perusahaan, "email": penyelia_email}
            )
            if not created:
                # Jika penyelia sudah ada, pastikan datanya diperbarui
                penyelia.perusahaan = penyelia_perusahaan
                penyelia.email = penyelia_email
                penyelia.save()

            instance.penyelia = penyelia

        if commit:
            instance.save()

        return instance
