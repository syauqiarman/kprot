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
            'sks_lulus': 'Jumlah SKS yang lulus saat ini',
            'pernyataan_komitmen': 'Saya menyatakan bahwa semua informasi yang diberikan benar dan bersedia mengikuti program hingga selesai',
        }
        widgets = {
            'sks_lulus': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent',
                'min': 0
            }),
            'jumlah_semester': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent',
                'min': 1
            }),
            'pernyataan_komitmen': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-gray-600 border-gray-300 rounded focus:ring-gray-500'
            }),
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
        mahasiswa = self.user.mahasiswa
        semester = cleaned_data.get('semester')

        if PendaftaranKP.objects.filter(mahasiswa=mahasiswa, semester=semester).exists():
            raise ValidationError("Anda sudah mendaftar di semester ini.")
        
        # Validasi jumlah semester dan SKS
        if (sks_lulus and sks_lulus < 100):
            raise ValidationError("Jumlah SKS lulus untuk mendaftar KP harus antara 100 hingga 144.")

        if (jumlah_semester and jumlah_semester < 6):
            raise ValidationError("Jumlah semester untuk mendaftar KP harus antara 6 hingga 12.")
        
        return cleaned_data

