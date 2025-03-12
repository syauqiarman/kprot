from django import forms
from django.core.exceptions import ValidationError
from database.models import PendaftaranKP, Semester


class PendaftaranKPForm(forms.ModelForm):
    nama = forms.CharField(disabled=True, required=False, label="Nama Mahasiswa")
    npm = forms.CharField(disabled=True, required=False, label="NPM")
    email = forms.EmailField(disabled=True, required=False, label="Email Mahasiswa")

    class Meta:
        model = PendaftaranKP
        fields = [
            'nama', 'npm', 'email',
            'semester', 'jumlah_semester', 'sks_lulus', 'pernyataan_komitmen',
        ]
        labels = {
            'jumlah_semester': 'Jumlah Semester yang Telah Ditempuh',
            'pernyataan_komitmen': 'Saya menyetujui pernyataan komitmen',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user and hasattr(self.user, 'mahasiswa'):
            mahasiswa = self.user.mahasiswa
            self.fields['nama'].initial = mahasiswa.nama
            self.fields['npm'].initial = mahasiswa.npm
            self.fields['email'].initial = mahasiswa.email

        semester_aktif = Semester.objects.filter(aktif=True).first()
        if semester_aktif:
            self.fields['semester'].initial = semester_aktif
            self.fields['semester'].disabled = True
        
    def clean(self):
        cleaned_data = super().clean()
        jumlah_semester = cleaned_data.get('jumlah_semester')
        sks_lulus = cleaned_data.get('sks_lulus')

        # Validasi jumlah semester dan SKS
        if (sks_lulus and sks_lulus < 100):
            raise ValidationError("Jumlah SKS lulus untuk mendaftar KP harus antara 100 hingga 144.")

        if (jumlah_semester and jumlah_semester < 6):
            raise ValidationError("Jumlah semester untuk mendaftar KP harus antara 6 hingga 12.")
        
        return cleaned_data

