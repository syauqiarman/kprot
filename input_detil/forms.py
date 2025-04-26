from django import forms
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from .models import PendaftaranKP, Penyelia, Semester, User

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
    prodi = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), required=False)
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
            self.fields['prodi'].initial = getattr(self.pendaftaran_kp.mahasiswa, "prodi", "")
            self.fields['semester'].initial = getattr(self.pendaftaran_kp.semester, "nama", "")
            self.fields['sks_lulus'].initial = getattr(self.pendaftaran_kp, "sks_lulus", 0)

    def clean(self):
        cleaned_data = super().clean()

        # Hapus field readonly agar tidak masuk ke cleaned_data
        readonly_fields = ["mahasiswa", "npm", "semester", "prodi", "sks_lulus"]
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
            existing_penyelia = Penyelia.objects.filter(email=penyelia_email).first()
            if existing_penyelia:
                # Update data jika perlu
                existing_penyelia.nama = penyelia_nama
                existing_penyelia.perusahaan = penyelia_perusahaan
                existing_penyelia.save()
                penyelia = existing_penyelia
            else:
                # Cek apakah user sudah ada
                user2 = User.objects.filter(email=penyelia_email).first()
                if user2:
                    # Cek apakah user sudah punya role lain (tapi belum jadi Penyelia)
                    raise forms.ValidationError("User sudah memiliki role lain dan tidak bisa menjadi Penyelia.")
                else:
                    # Buat user baru
                    username = penyelia_email.split('@')[0]
                    user2 = User.objects.create(email=penyelia_email, username=username)
                    temporary_password = get_random_string(length=10)
                    user2.set_password(temporary_password)
                    user2.save()
                    # Buat Penyelia baru
                    penyelia = Penyelia.objects.create(
                        user=user2,
                        nama=penyelia_nama,
                        perusahaan=penyelia_perusahaan,
                        email=penyelia_email
                    )

                    print("tes masuk")
                    send_mail(
                        subject='Test Email',
                        message=(
                            f"Halo {penyelia_nama},\n\n"
                            f"Akun Anda sebagai penyelia telah berhasil didaftarkan.\n"
                            f"Silakan login dengan kredensial berikut:\n\n"
                            f"Username: {penyelia_email}\n"
                            f"Password sementara: {temporary_password}\n\n"
                            f"Harap segera login dan ganti password Anda.\n\n"
                            f"Terima kasih."
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[penyelia_email],
                        fail_silently=False,
                    )
                    print("tes keluar")

            # Set penyelia ke instance form
            instance.penyelia = penyelia

        if commit:
            instance.save()

        return instance