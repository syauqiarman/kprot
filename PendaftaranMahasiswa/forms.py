from django import forms
from PendaftaranMahasiswa.validators import validate_jumlah_semester_kp, validate_sks_lulus
from .models import PendaftaranKP

class PendaftaranKPForm(forms.ModelForm):
    class Meta:
        model = PendaftaranKP
        fields = ['mahasiswa', 'semester', 'jumlah_semester', 'sks_lulus', 'pernyataan_komitmen']

    # Readonly fields (not saved in model)
    mahasiswa = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), required=False)
    npm = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), required=False)
    semester = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), required=False)
    
    jumlah_semester = forms.IntegerField(
        validators=[validate_jumlah_semester_kp],
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 6, "max": 12})
    )
    sks_lulus = forms.IntegerField(
        validators=[validate_sks_lulus],
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 100, "max": 144})
    )
    pernyataan_komitmen = forms.BooleanField(
        required=True,
        label="Saya menyetujui pernyataan komitmen",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )
    status_pendaftaran = forms.CharField(
        max_length=50,
        initial="Menunggu Detil",
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        mahasiswa = kwargs.pop('mahasiswa', None)
        semester = kwargs.pop('semester', None)   # Get mahasiswa instance if provided
        super().__init__(*args, **kwargs)

        if mahasiswa:
            self.fields['mahasiswa'].initial = mahasiswa.nama
            self.fields['npm'].initial = mahasiswa.npm
        if semester:
            self.fields['semester'].initial = semester.nama


    def clean(self):
        cleaned_data = super().clean()
        cleaned_data["status_pendaftaran"] = "Menunggu Detil"  # Set otomatis ke "Menunggu Detil"
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.status_pendaftaran = "Menunggu Detil"  # Tetap set default status
        if commit:
            instance.save()
        return instance
