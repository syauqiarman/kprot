from django import forms
from django.forms import ValidationError, inlineformset_factory
from database.models import LogMingguan, AktivitasHarian

class LogMingguanForm(forms.ModelForm):
    nama = forms.CharField(disabled=True, required=False)
    npm = forms.CharField(disabled=True, required=False)
    tempat_magang = forms.CharField(disabled=True, required=False)
    role_magang = forms.CharField(disabled=True, required=False)

    class Meta:
        model = LogMingguan
        fields = ['minggu_ke', 'tanggal_mulai', 'tanggal_selesai']
        widgets = {
            'tanggal_mulai': forms.DateInput(attrs={'type': 'date'}),
            'tanggal_selesai': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.program = kwargs.pop('program', None)
        super().__init__(*args, **kwargs)
        
        if self.program:
            # Ambil data dari program
            self.fields['tempat_magang'].initial = self.program.penyelia.perusahaan
            self.fields['role_magang'].initial = self.program.role
            self.fields['nama'].initial = self.program.mahasiswa.nama
            self.fields['npm'].initial = self.program.mahasiswa.npm

    def clean(self):
        cleaned_data = super().clean()
        tanggal_mulai = cleaned_data.get('tanggal_mulai')
        tanggal_selesai = cleaned_data.get('tanggal_selesai')
        
        if not tanggal_mulai or not tanggal_selesai:
            raise ValidationError("Tanggal mulai dan selesai harus diisi")
        
        if tanggal_mulai > tanggal_selesai:
            raise ValidationError("Tanggal mulai harus sebelum tanggal selesai")

AktivitasFormSet = inlineformset_factory(
    LogMingguan, AktivitasHarian,
    fields=('tanggal', 'jam_mulai', 'jam_selesai', 'deskripsi'),
    extra=1,
    widgets={
        'tanggal': forms.DateInput(attrs={'type': 'date'}),
        'jam_mulai': forms.TimeInput(attrs={'type': 'time'}),
        'jam_selesai': forms.TimeInput(attrs={'type': 'time'}),
        'deskripsi': forms.Textarea(attrs={'rows': 2}),
    }
)