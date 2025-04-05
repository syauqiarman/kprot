from django import forms
from database.models import LogMingguan, AktivitasHarian
from django.forms import inlineformset_factory

class LogMingguanForm(forms.ModelForm):
    nama = forms.CharField(disabled=True, required=False)
    npm = forms.CharField(disabled=True, required=False)
    tempat_magang = forms.CharField(disabled=True, required=False)
    role_magang = forms.CharField(disabled=True, required=False)

    class Meta:
        model = LogMingguan
        fields = ['tanggal_mulai', 'tanggal_selesai']
        
    def __init__(self, *args, **kwargs):
        self.program = kwargs.pop('program', None)
        super().__init__(*args, **kwargs)
        if self.program:
            mahasiswa = self.program.mahasiswa
            self.fields['nama'].initial = mahasiswa.nama
            self.fields['npm'].initial = mahasiswa.npm
            self.fields['tempat_magang'].initial = self.program.penyelia.perusahaan
            self.fields['role_magang'].initial = self.program.role
    
    def clean(self):
        cleaned_data = super().clean()
        tanggal_mulai = cleaned_data.get('tanggal_mulai')
        tanggal_selesai = cleaned_data.get('tanggal_selesai')

        if tanggal_mulai and tanggal_selesai:
            if tanggal_mulai > tanggal_selesai:
                self.add_error('tanggal_mulai', "Tanggal mulai tidak boleh setelah tanggal selesai")
                self.add_error('tanggal_selesai', "Tanggal selesai tidak boleh sebelum tanggal mulai")

        return cleaned_data

class AktivitasHarianForm(forms.ModelForm):
    class Meta:
        model = AktivitasHarian
        fields = ['tanggal', 'jam_mulai', 'jam_selesai', 'deskripsi']
        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date'}),
            'jam_mulai': forms.TimeInput(attrs={'type': 'time'}),
            'jam_selesai': forms.TimeInput(attrs={'type': 'time'}),
        }

AktivitasHarianFormSet = inlineformset_factory(
    LogMingguan,
    AktivitasHarian,
    form=AktivitasHarianForm,
    extra=7,  # Default untuk 1 minggu
    can_delete=False
)