from django import forms
from database.models import PendaftaranMBKM, PendaftaranKP, Penyelia, ProgramMBKM, User, validate_tanggal_mulai_selesai
from django.core.exceptions import ValidationError
from database.validators import validate_email_penyelia
import secrets

class InputDetilMBKMForm(forms.ModelForm):
    class Meta:
        model = PendaftaranMBKM
        fields = ['role', 'program_mbkm', 'tanggal_mulai', 'tanggal_selesai']

        widgets = {
            'tanggal_mulai': forms.DateInput(attrs={'type': 'date'}),
            'tanggal_selesai': forms.DateInput(attrs={'type': 'date'}),
        }

    mahasiswa_nama = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), required=False)
    mahasiswa_npm = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), required=False)
    semester = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), required=False)

    penyelia_nama = forms.CharField(widget=forms.TextInput(), required=True)
    penyelia_email = forms.EmailField(widget=forms.EmailInput(), required=True)
    penyelia_perusahaan = forms.CharField(widget=forms.TextInput(), required=True)

    program_mbkm = forms.ModelChoiceField(
        queryset=ProgramMBKM.objects.all(),
        widget=forms.RadioSelect(attrs={'class': 'flex space-x-4'})
    )

    def __init__(self, *args, **kwargs):
        self.pendaftaran_mbkm = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        if self.pendaftaran_mbkm:
            mahasiswa = getattr(self.pendaftaran_mbkm, "mahasiswa", None)
            semester = getattr(self.pendaftaran_mbkm, "semester", None)

            self.fields['mahasiswa_nama'].initial = getattr(mahasiswa, "nama", "")
            self.fields['mahasiswa_npm'].initial = getattr(mahasiswa, "npm", "")
            self.fields['semester'].initial = getattr(semester, "nama", "")

    def clean(self):
        cleaned_data = super().clean()

        # Validate penyelia_email using the validator
        penyelia_email = cleaned_data.get('penyelia_email')
        if penyelia_email:
            try:
                validate_email_penyelia(penyelia_email)
            except ValidationError as e:
                self.add_error('penyelia_email', e)

        # Validate tanggal_mulai and tanggal_selesai using the model validation function
        try:
            validate_tanggal_mulai_selesai(self.instance)
        except ValidationError as e:
            self.add_error(None, e)  # Add the error to the form's non-field errors

        # Ensure tanggal_mulai is before tanggal_selesai
        tanggal_mulai = cleaned_data.get('tanggal_mulai')
        tanggal_selesai = cleaned_data.get('tanggal_selesai')
        if tanggal_mulai and tanggal_selesai and tanggal_mulai > tanggal_selesai:
            self.add_error('tanggal_selesai', "Tanggal mulai tidak boleh setelah tanggal selesai.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Update status_pendaftaran based on completeness
        required_fields = ["role", "program_mbkm", "penyelia_nama", "penyelia_perusahaan", "penyelia_email", "tanggal_mulai", "tanggal_selesai"]
        is_complete = all(self.cleaned_data.get(field) for field in required_fields)
        instance.status_pendaftaran = "Terdaftar" if is_complete else "Menunggu Detil"

        # Create or update Penyelia
        penyelia_nama = self.cleaned_data.get("penyelia_nama")
        penyelia_perusahaan = self.cleaned_data.get("penyelia_perusahaan")
        penyelia_email = self.cleaned_data.get("penyelia_email")

        if penyelia_nama and penyelia_perusahaan and penyelia_email:
            user2 = User.objects.filter(email=penyelia_email).first()

            if user2:
                if Penyelia.objects.filter(user=user2).exists():
                    penyelia = Penyelia.objects.get(user=user2)
                else:
                    raise forms.ValidationError("User sudah memiliki role lain dan tidak bisa menjadi Penyelia.")
            else:
                user2 = User.objects.create(email=penyelia_email, username=penyelia_email)
                penyelia = Penyelia.objects.create(
                    user=user2,
                    nama=penyelia_nama,
                    perusahaan=penyelia_perusahaan,
                    email=penyelia_email
                )

            instance.penyelia = penyelia

        if commit:
            instance.save()

        return instance

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
            self.add_error("tanggal_selesai", "Tanggal selesai harus setelah tanggal mulai.")


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

        if penyelia_nama and penyelia_perusahaan and penyelia_email:
            # Cek apakah user dengan email ini sudah ada
            print("di cek user")
            user2 = User.objects.filter(email=penyelia_email).first()

            if user2:
                # Cek apakah user sudah memiliki role lain
                if Penyelia.objects.filter(user=user2).exists():
                    penyelia = Penyelia.objects.get(user=user2)
                else:
                    raise forms.ValidationError("User sudah memiliki role lain dan tidak bisa menjadi Penyelia.")
            else:
                # Jika user belum ada, buat user baru
                user2 = User.objects.create(email=penyelia_email, username=penyelia_email)

                # Buat Penyelia baru
                penyelia = Penyelia.objects.create(
                    user=user2,
                    nama=penyelia_nama,
                    perusahaan=penyelia_perusahaan,
                    email=penyelia_email
                )

            # Set penyelia ke instance form
            instance.penyelia = penyelia

        if commit:
            instance.save()

        return instance