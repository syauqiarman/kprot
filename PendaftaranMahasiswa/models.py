from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

class Mahasiswa(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    nama = models.CharField(max_length=255)
    npm = models.CharField(max_length=20, unique=True)

class PembimbingAkademik(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    nama = models.CharField(max_length=255)

class Kaprodi(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    nama = models.CharField(max_length=255)

class ManajemenFakultas(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    nama = models.CharField(max_length=255)

class Penyelia(models.Model):
    nama = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    perusahaan = models.CharField(max_length=255)

class Semester(models.Model):
    semester = models.CharField(max_length=16, unique=True)
    aktif = models.BooleanField(default=False)
    gasal_genap = models.CharField(max_length=5)  

class ProgramMBKM(models.Model):
    nama = models.CharField(max_length=255)
    minimum_sks = models.IntegerField()
    maksimum_sks = models.IntegerField()

class PendaftaranKP(models.Model):
    mahasiswa = models.ForeignKey(Mahasiswa, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    jumlah_semester = models.IntegerField()
    sks_diambil = models.IntegerField()
    sks_lulus = models.IntegerField()
    penyelia = models.ForeignKey(Penyelia, on_delete=models.CASCADE)
    role = models.CharField(max_length=255)
    total_jam_kerja = models.IntegerField()
    tanggal_mulai = models.DateField()
    tanggal_selesai = models.DateField()
    pernyataan_komitmen = models.BooleanField(default=False)
    status_pendaftaran = models.CharField(max_length=50)
    history = models.JSONField(default=list)

class PendaftaranMBKM(models.Model):
    mahasiswa = models.ForeignKey(Mahasiswa, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    jumlah_semester = models.IntegerField()
    sks_diambil = models.IntegerField()
    request_status_merdeka = models.BooleanField(default=False)
    rencana_lulus_semester_ini = models.BooleanField(default=False)
    program_mbkm = models.ForeignKey(ProgramMBKM, on_delete=models.CASCADE)
    penyelia = models.ForeignKey(Penyelia, on_delete=models.CASCADE)
    role = models.CharField(max_length=255)
    estimasi_sks_konversi = models.IntegerField()
    persetujuan_pa = models.FileField(upload_to='persetujuan_pa/', blank=True, null=True)
    tanggal_persetujuan = models.DateField(blank=True, null=True)
    tanggal_mulai = models.DateField()
    tanggal_selesai = models.DateField()
    pernyataan_komitmen = models.BooleanField(default=False)
    status_pendaftaran = models.CharField(max_length=50)
    history = models.JSONField(default=list)
    file_timestamp = models.DateTimeField(null=True, blank=True)