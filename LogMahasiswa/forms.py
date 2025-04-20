from django import forms
from database.models import Aktivitas, Hari, LogMingguan, PendaftaranKP, PendaftaranMBKM
from django.forms import ValidationError, inlineformset_factory, BaseInlineFormSet

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
        date_attrs = {
            'type': 'date',
            'class': 'border rounded p-2 w-full focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'min': self.program.tanggal_mulai.strftime('%Y-%m-%d'),
            'max': self.program.tanggal_selesai.strftime('%Y-%m-%d')
        }
        
        self.fields['tanggal_mulai'].widget = forms.DateInput(attrs=date_attrs)
        self.fields['tanggal_selesai'].widget = forms.DateInput(attrs=date_attrs)

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
        program = self.program

        if tanggal_mulai and tanggal_selesai:

            delta = tanggal_selesai - tanggal_mulai
            if delta.days > 6:  # 7 hari inklusif
                self.add_error(
                    'tanggal_selesai',
                    "Maksimal rentang log mingguan adalah 7 hari"
                )

            if tanggal_mulai > tanggal_selesai:
                self.add_error('tanggal_mulai', "Tanggal mulai tidak boleh setelah tanggal selesai")
                self.add_error('tanggal_selesai', "Tanggal selesai tidak boleh sebelum tanggal mulai")
            
            if not (program.tanggal_mulai <= tanggal_mulai <= program.tanggal_selesai):
                self.add_error('tanggal_mulai', "Tanggal mulai log di luar periode program")
            
            if not (program.tanggal_mulai <= tanggal_selesai <= program.tanggal_selesai):
                self.add_error('tanggal_selesai', "Tanggal selesai log di luar periode program")

            if program.status_pendaftaran != "Terdaftar":
                self.add_error(None, "Program harus dalam status Terdaftar untuk membuat log")
            
            # Tentukan filter berdasarkan tipe program
            if isinstance(program, PendaftaranKP):
                field_filter = {'pendaftaran_kp': program}
            elif isinstance(program, PendaftaranMBKM):
                field_filter = {'pendaftaran_mbkm': program}
            else:
                raise ValidationError("Jenis program tidak valid")

            # Validasi overlap
            existing_logs = LogMingguan.objects.filter(
                **field_filter,
                tanggal_mulai__lte=tanggal_selesai,
                tanggal_selesai__gte=tanggal_mulai
            )
            
            if self.instance.pk:
                existing_logs = existing_logs.exclude(pk=self.instance.pk)
                
            if existing_logs.exists():
                self.add_error(None, "Periode log ini tumpang tindih dengan log yang sudah ada")
                
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.pk:  # Jika objek baru
            if isinstance(self.program, PendaftaranKP):
                instance.pendaftaran_kp = self.program
            else:
                instance.pendaftaran_mbkm = self.program
        if commit:
            instance.save()
        return instance

class AktivitasForm(forms.ModelForm):
    class Meta:
        model = Aktivitas
        fields = ['jam_mulai', 'jam_selesai', 'deskripsi']
        widgets = {
            'jam_mulai': forms.TimeInput(attrs={'type': 'time', 'class': 'border rounded p-2 w-full'}),
            'jam_selesai': forms.TimeInput(attrs={'type': 'time', 'class': 'border rounded p-2 w-full'}),
            'deskripsi': forms.Textarea(attrs={'rows': 2, 'class': 'border rounded p-2 w-full'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        jam_mulai = cleaned_data.get('jam_mulai')
        jam_selesai = cleaned_data.get('jam_selesai')
        
        if jam_mulai and jam_selesai:
            if jam_mulai >= jam_selesai:
                self.add_error('jam_selesai', 'Jam selesai harus setelah jam mulai')
            
            # Cek overlap waktu dalam hari yang sama
            existing_aktivitas = Aktivitas.objects.filter(
                hari=self.instance.hari,
                jam_mulai__lt=jam_selesai,
                jam_selesai__gt=jam_mulai
            ).exclude(pk=self.instance.pk)
            
            if existing_aktivitas.exists():
                self.add_error(None, 'Waktu aktivitas bertabrakan dengan aktivitas lain')

AktivitasFormSet = inlineformset_factory(
    Hari,
    Aktivitas,
    form=AktivitasForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)

class BaseHariFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.log_mingguan = kwargs.pop('log_mingguan', None)
        super().__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['log_mingguan'] = self.log_mingguan
        return kwargs

HariFormSet = inlineformset_factory(
    LogMingguan,
    Hari,
    fields=('tanggal',),
    extra=0,
    can_delete=False,
    formset=BaseHariFormSet
)