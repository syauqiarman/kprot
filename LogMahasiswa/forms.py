from django import forms
from database.models import LogMingguan, AktivitasHarian, PendaftaranKP, PendaftaranMBKM
from django.forms import ValidationError, inlineformset_factory, BaseInlineFormSet
from datetime import date

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

        if tanggal_mulai and tanggal_selesai:
            today = date.today()
            if tanggal_mulai > today or tanggal_selesai > today:
                raise ValidationError("Tidak dapat membuat log untuk tanggal di masa depan")

            delta = tanggal_selesai - tanggal_mulai
            if delta.days > 6:  # 7 hari inklusif
                self.add_error(
                    'tanggal_selesai',
                    "Maksimal rentang log mingguan adalah 7 hari"
                )

            if tanggal_mulai > tanggal_selesai:
                self.add_error('tanggal_mulai', "Tanggal mulai tidak boleh setelah tanggal selesai")
                self.add_error('tanggal_selesai', "Tanggal selesai tidak boleh sebelum tanggal mulai")
            
            if not (self.program.tanggal_mulai <= tanggal_mulai <= self.program.tanggal_selesai):
                self.add_error('tanggal_mulai', "Tanggal mulai log di luar periode program")
            
            if not (self.program.tanggal_mulai <= tanggal_selesai <= self.program.tanggal_selesai):
                self.add_error('tanggal_selesai', "Tanggal selesai log di luar periode program")

            if self.program.status_pendaftaran != "Terdaftar":
                self.add_error(None, "Program harus dalam status Terdaftar untuk membuat log")
            
            # Tentukan filter berdasarkan tipe program
            if isinstance(self.program, PendaftaranKP):
                field_filter = {'pendaftaran_kp': self.program}
            elif isinstance(self.program, PendaftaranMBKM):
                field_filter = {'pendaftaran_mbkm': self.program}
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

class BaseAktivitasHarianFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if not self.is_valid():
            return

        activities_per_day = {}
        
        for form in self.forms:
            if self.can_delete and form.cleaned_data.get('DELETE'):
                continue
                
            tanggal = form.cleaned_data.get('tanggal')
            jam_mulai = form.cleaned_data.get('jam_mulai')
            jam_selesai = form.cleaned_data.get('jam_selesai')
            
            if tanggal:
                if tanggal not in activities_per_day:
                    activities_per_day[tanggal] = []
                activities_per_day[tanggal].append((jam_mulai, jam_selesai))

        # Must have at least one activity after deletions
        if not any(not form.cleaned_data.get('DELETE', False) for form in self.forms):
            raise ValidationError('Harus ada minimal satu aktivitas')

        # Check max activities and overlapping times per day
        for tanggal, aktivitas in activities_per_day.items():
            if len(aktivitas) > 5:
                raise ValidationError('Maksimal 5 aktivitas per hari')

            # Check overlapping times
            aktivitas.sort()
            for i in range(len(aktivitas)-1):
                if aktivitas[i][1] > aktivitas[i+1][0]:
                    raise ValidationError('Waktu aktivitas tidak boleh tumpang tindih')

class AktivitasHarianForm(forms.ModelForm):
    class Meta:
        model = AktivitasHarian
        fields = ['tanggal', 'jam_mulai', 'jam_selesai', 'deskripsi']

    def clean(self):
        cleaned_data = super().clean()
        tanggal = cleaned_data.get('tanggal')
        jam_mulai = cleaned_data.get('jam_mulai')
        jam_selesai = cleaned_data.get('jam_selesai')
        
        if all([tanggal, jam_mulai, jam_selesai]):
            # Validate time range
            if jam_mulai >= jam_selesai:
                raise ValidationError({
                    'jam_mulai': 'Jam mulai harus sebelum jam selesai'
                })

            # Validate date range if we have a log instance
            if hasattr(self, 'instance') and self.instance.log_mingguan_id:
                log = self.instance.log_mingguan
                if not (log.tanggal_mulai <= tanggal <= log.tanggal_selesai):
                    raise ValidationError({
                        'tanggal': 'Tanggal aktivitas harus dalam rentang log mingguan'
                    })

            # Validate future dates
            today = date.today()
            if tanggal > today:
                raise ValidationError({
                    'tanggal': 'Tidak dapat membuat aktivitas untuk tanggal di masa depan'
                })

        return cleaned_data

AktivitasHarianFormSet = inlineformset_factory(
    LogMingguan,
    AktivitasHarian,
    form=AktivitasHarianForm,
    formset=BaseAktivitasHarianFormSet,
    extra=0,
    can_delete=True,
    validate_min=True,
    min_num=1,
    validate_max=True,
    max_num=35  # 5 activities * 7 days
)