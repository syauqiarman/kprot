from django import forms
from database.models import LogMingguan, AktivitasHarian, PendaftaranKP, PendaftaranMBKM
from django.forms import BaseInlineFormSet, ValidationError, inlineformset_factory

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
            self._validate_date_range(tanggal_mulai, tanggal_selesai)
            self._validate_program_dates(tanggal_mulai, tanggal_selesai, program)
            self._validate_program_status(program)
            self._validate_overlap(tanggal_mulai, tanggal_selesai, program)

        return cleaned_data

    def _validate_date_range(self, tanggal_mulai, tanggal_selesai):
        delta = tanggal_selesai - tanggal_mulai
        if delta.days > 6:  # 7 hari inklusif
            self.add_error(
                'tanggal_selesai',
                "Maksimal rentang log mingguan adalah 7 hari"
            )

        if tanggal_mulai > tanggal_selesai:
            self.add_error('tanggal_mulai', "Tanggal mulai tidak boleh setelah tanggal selesai")
            self.add_error('tanggal_selesai', "Tanggal selesai tidak boleh sebelum tanggal mulai")

    def _validate_program_dates(self, tanggal_mulai, tanggal_selesai, program):
        if not (program.tanggal_mulai <= tanggal_mulai <= program.tanggal_selesai):
            self.add_error('tanggal_mulai', "Tanggal mulai log di luar periode program")

        if not (program.tanggal_mulai <= tanggal_selesai <= program.tanggal_selesai):
            self.add_error('tanggal_selesai', "Tanggal selesai log di luar periode program")

    def _validate_program_status(self, program):
        if program.status_pendaftaran != "Terdaftar":
            self.add_error(None, "Program harus dalam status Terdaftar untuk membuat log")

    def _validate_overlap(self, tanggal_mulai, tanggal_selesai, program):
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

class BaseAktivitasHarianFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_mingguan = self.instance  # Simpan instance LogMingguan

    def _construct_form(self, i, **kwargs):
        kwargs['log_mingguan'] = self.log_mingguan  # Pass ke setiap form
        return super()._construct_form(i, **kwargs)

COMMON_INPUT_CSS_CLASS = 'border rounded p-2 w-full'

class AktivitasHarianForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.log_mingguan = kwargs.pop('log_mingguan', None)  # Terima log_mingguan
        super().__init__(*args, **kwargs)

    class Meta:
        model = AktivitasHarian
        fields = ['tanggal', 'jam_mulai', 'jam_selesai', 'deskripsi']
        widgets = {
            'tanggal': forms.DateInput(attrs={
                'type': 'date',
                'class': COMMON_INPUT_CSS_CLASS
            }),
            'jam_mulai': forms.TimeInput(attrs={
                'type': 'time',
                'class': COMMON_INPUT_CSS_CLASS, 
                'step': '60'
            }),
            'jam_selesai': forms.TimeInput(attrs={
                'type': 'time',
                'class': COMMON_INPUT_CSS_CLASS, 
                'step': '60'
            }),
            'deskripsi': forms.Textarea(attrs={
                'rows': 2,
                'class': COMMON_INPUT_CSS_CLASS
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        tanggal = cleaned_data.get('tanggal')
        log = self.log_mingguan
        
        if log.tanggal_mulai is not None and log.tanggal_selesai is not None:
            if not (log.tanggal_mulai <= tanggal <= log.tanggal_selesai):
                self.add_error('tanggal', "Tanggal aktivitas harus dalam periode log mingguan")
        
        jam_mulai = cleaned_data.get('jam_mulai')
        jam_selesai = cleaned_data.get('jam_selesai')
        if jam_mulai and jam_selesai and jam_mulai >= jam_selesai:
            self.add_error('jam_mulai', "Jam mulai harus sebelum jam selesai")

AktivitasHarianFormSet = inlineformset_factory(
    LogMingguan,
    AktivitasHarian,
    form=AktivitasHarianForm,
    extra=7,
    can_delete=True,  # Ubah menjadi True
    validate_min=True,
    formset=BaseAktivitasHarianFormSet
)