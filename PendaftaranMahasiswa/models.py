from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils.translation import gettext_lazy as _

from .validators import *

############################# Abstract models #############################

class OneRoleUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nama = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        validate_one_role_user(self.user)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class MultiRolesUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nama = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        validate_multi_roles_user(self.user)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

###########################################################################

class Dosen(MultiRolesUser):
    pass

class PembimbingAkademik(MultiRolesUser):
    pass

class Kaprodi(MultiRolesUser):
    pass

class ManajemenFakultas(MultiRolesUser):
    pass

class Mahasiswa(OneRoleUser):
    npm = models.CharField(max_length=20, unique=True)
    pa = models.ForeignKey(PembimbingAkademik, on_delete=models.CASCADE, blank=True, null=True)

class Penyelia(OneRoleUser):
    email = models.EmailField(unique=True, validators=[validate_email_penyelia])
    perusahaan = models.CharField(max_length=255)

class Semester(models.Model):
    nama = models.CharField(max_length=16, unique=True)
    gasal_genap = models.CharField(max_length=5)  
    tahun = models.IntegerField()
    aktif = models.BooleanField(default=False)

    def __str__(self):
        return self.nama

class ProgramMBKM(models.Model):
    nama = models.CharField(max_length=255)
    minimum_sks = models.IntegerField()
    maksimum_sks = models.IntegerField()

class PendaftaranKP(models.Model):
    mahasiswa = models.ForeignKey(Mahasiswa, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    jumlah_semester = models.IntegerField(validators=[validate_jumlah_semester_kp])
    sks_lulus = models.IntegerField(validators=[validate_sks_lulus])
    penyelia = models.ForeignKey(Penyelia, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=255, null=True, blank=True)
    total_jam_kerja = models.IntegerField(validators=[validate_total_jam_kerja], null=True, blank=True)
    tanggal_mulai = models.DateField(null=True, blank=True)
    tanggal_selesai = models.DateField(null=True, blank=True)
    pernyataan_komitmen = models.BooleanField(default=False, validators=[validate_pernyataan_komitmen])
    status_pendaftaran = models.CharField(max_length=50, default="Menunggu Detil", choices=[
            ('Menunggu Detil', 'Menunggu Detil'),
            ('Terdaftar', 'Terdaftar')
    ])
    history = models.JSONField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.pk:
            self.history = [datetime.now().isoformat()]

    def clean(self):
        super().clean()
        validate_tanggal_mulai_selesai(self)
        validate_jika_terdaftar(self)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class PendaftaranMBKM(models.Model):
    mahasiswa = models.ForeignKey(Mahasiswa, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    jumlah_semester = models.IntegerField(validators=[validate_jumlah_semester_mbkm])
    sks_diambil = models.IntegerField(validators=[validate_sks_diambil], blank=True, null=True)
    request_status_merdeka = models.BooleanField(default=False)
    rencana_lulus_semester_ini = models.BooleanField(default=False)
    program_mbkm = models.ForeignKey(ProgramMBKM, on_delete=models.CASCADE)
    penyelia = models.ForeignKey(Penyelia, on_delete=models.CASCADE, blank=True, null=True)
    role = models.CharField(max_length=255, blank=True, null=True)
    estimasi_sks_konversi = models.IntegerField(blank=True, null=True)
    persetujuan_pa = models.FileField(upload_to='persetujuan_pa/', blank=True, null=True)
    tanggal_persetujuan = models.DateField(blank=True, null=True)
    tanggal_mulai = models.DateField(blank=True, null=True)
    tanggal_selesai = models.DateField(blank=True, null=True)
    pernyataan_komitmen = models.BooleanField(default=False, validators=[validate_pernyataan_komitmen])
    status_pendaftaran = models.CharField(max_length=50, default="Menunggu Persetujuan PA", choices=[
            ('Menunggu Persetujuan PA', 'Menunggu Persetujuan PA'),
            ('Ditolak PA', 'Ditolak PA'),
            ('Menunggu Persetujuan Kaprodi', 'Menunggu Persetujuan Kaprodi'),
            ('Ditolak Kaprodi', 'Ditolak Kaprodi'),
            ('Menunggu Verifikasi Dosen', 'Menunggu Verifikasi Dosen'),
            ('Ditolak Dosen', 'Ditolak Dosen'),
            ('Menunggu Detil', 'Menunggu Detil'),
            ('Terdaftar', 'Terdaftar'),
        ]
    )
    feedback_penolakan = models.TextField(blank=True, null=True)
    history = models.JSONField()
    file_timestamp = models.DateTimeField(null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_status_merdeka = self.sks_diambil == 0
        if not self.pk:
            if self.persetujuan_pa:
                self.status_pendaftaran = "Menunggu Verifikasi Dosen"
            else:
                self.status_pendaftaran = "Menunggu Persetujuan PA"
            self.history = [datetime.now().isoformat()]

    def clean(self):
        super().clean()
        validate_estimasi_sks_konversi(self) 
        validate_tanggal_mulai_selesai(self)
        validate_jika_terdaftar(self)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

############## Validators that can't be in validators.py ##############

def validate_one_role_user(user):
    user_has_any_role = (
        Mahasiswa.objects.filter(user=user).exists() or
        Penyelia.objects.filter(user=user).exists() or
        Dosen.objects.filter(user=user).exists() or
        PembimbingAkademik.objects.filter(user=user).exists() or
        Kaprodi.objects.filter(user=user).exists() or
        ManajemenFakultas.objects.filter(user=user).exists()
    )
    if user_has_any_role:
        raise ValidationError("User sudah memiliki role lain.")
    
def validate_multi_roles_user(user):
    if Mahasiswa.objects.filter(user=user).exists():
        raise ValidationError(_("User sudah memiliki role Mahasiswa."))
    elif Penyelia.objects.filter(user=user).exists():
        raise ValidationError(_("User sudah memiliki role Penyelia."))
    
def validate_tanggal_mulai_selesai(instance):
    # Ensure tanggal_mulai and tanggal_selesai are not None before validation
    if instance.tanggal_mulai is None or instance.tanggal_selesai is None:
        return  # Skip validation if either date is missing

    start_date = {PendaftaranKP: {"Genap": date(instance.semester.tahun-1, 10, 1),
                                  "Gasal": date(instance.semester.tahun, 4, 1)}, 
                  PendaftaranMBKM: {"Genap": date(instance.semester.tahun, 1, 1),
                                    "Gasal": date(instance.semester.tahun, 7, 1)}}
    
    end_date = {PendaftaranKP: {"Genap": date(instance.semester.tahun, 4, 30),
                                "Gasal": date(instance.semester.tahun, 10, 31)},
                PendaftaranMBKM: {"Genap": date(instance.semester.tahun, 6, 30),
                                  "Gasal": date(instance.semester.tahun+1, 1, 31)}}
    try:
        start_date = start_date[instance.__class__][instance.semester.gasal_genap]
        end_date = end_date[instance.__class__][instance.semester.gasal_genap]
    except KeyError:
        raise ValidationError(_("Semester harus bernilai 'Gasal' atau 'Genap'."))
    
    # Validate tanggal_mulai and tanggal_selesai within the correct semester range
    if not (start_date <= instance.tanggal_mulai <= end_date):
        raise ValidationError(_("Tanggal mulai harus antara {0} dan {1}.").format(start_date, end_date))
    if not (start_date <= instance.tanggal_selesai <= end_date):
        raise ValidationError(_("Tanggal selesai harus antara {0} dan {1}.").format(start_date, end_date))

    # Ensure tanggal_mulai is before tanggal_selesai
    if instance.tanggal_mulai > instance.tanggal_selesai:
        raise ValidationError(_("Tanggal mulai harus sebelum tanggal selesai."))
        
def validate_jika_terdaftar(instance):
    # check if instance is pendaftaran mbkm or pendaftaran kp
    if instance.status_pendaftaran != "Terdaftar":
        return 
    
    if isinstance(instance, PendaftaranKP):
        required_fields = [instance.penyelia, instance.role, instance.total_jam_kerja, 
                           instance.tanggal_mulai, instance.tanggal_selesai]
    elif isinstance(instance, PendaftaranMBKM):
        required_fields = [instance.penyelia, instance.role, instance.sks_diambil, 
                           instance.estimasi_sks_konversi, instance.tanggal_mulai,
                           instance.tanggal_selesai]
        
    if any(field is None or field == "" for field in required_fields):
        raise ValidationError(_("Semua bidang harus diisi sebelum status dapat diubah menjadi 'Terdaftar'."))