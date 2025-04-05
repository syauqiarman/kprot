from django import forms
from django.forms import inlineformset_factory
from database.models import LogMingguan, AktivitasHarian
from django.core.exceptions import ValidationError
from database.models import PendaftaranKP, PendaftaranMBKM

class LogMingguanForm(forms.ModelForm):
    class Meta:
        model = LogMingguan
        fields = ['tanggal_mulai', 'tanggal_selesai']
        widgets = {
            'tanggal_mulai': forms.DateInput(attrs={'type': 'date'}),
            'tanggal_selesai': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.program_kp = None
        self.program_mbkm = None
        if self.user and hasattr(self.user, 'mahasiswa'):
            self.program_kp = PendaftaranKP.objects.filter(
                mahasiswa=self.user.mahasiswa,
                status_pendaftaran='Terdaftar'
            ).first()
            self.program_mbkm = PendaftaranMBKM.objects.filter(
                mahasiswa=self.user.mahasiswa,
                status_pendaftaran='Terdaftar'
            ).first()
    
    def clean(self):
        cleaned_data = super().clean()
        if not (self.program_kp or self.program_mbkm):
            raise ValidationError("Anda belum terdaftar di program KP atau MBKM yang aktif.")
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.program_kp:
            instance.pendaftaran_kp = self.program_kp
        elif self.program_mbkm:
            instance.pendaftaran_mbkm = self.program_mbkm
        if commit:
            instance.save()
        return instance

class AktivitasHarianForm(forms.ModelForm):
    class Meta:
        model = AktivitasHarian
        fields = ['tanggal', 'jam_mulai', 'jam_selesai', 'deskripsi']
        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date'}),
            'jam_mulai': forms.TimeInput(attrs={'type': 'time'}),
            'jam_selesai': forms.TimeInput(attrs={'type': 'time'}),
            'deskripsi': forms.Textarea(attrs={'rows': 2}),
        }

AktivitasHarianFormSet = inlineformset_factory(
    LogMingguan, AktivitasHarian, form=AktivitasHarianForm,
    extra=1, can_delete=True, can_delete_extra=True
)