from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Mahasiswa)
class MahasiswaAdmin(admin.ModelAdmin):
    list_display = ('nama', 'npm', 'email', 'prodi', 'pa', 'user')
    search_fields = ('nama', 'npm', 'email')
    list_filter = ('prodi', 'pa', 'user')

@admin.register(ProgramMBKM)
class ProgramMBKMAdmin(admin.ModelAdmin):
    list_display = ('nama', 'minimum_sks', 'maksimum_sks')
    search_fields = ('nama',)

@admin.register(PendaftaranMBKM)
class PendaftaranMBKMAdmin(admin.ModelAdmin):
    list_display = ('mahasiswa', 'program_mbkm', 'status_pendaftaran')
    search_fields = ('mahasiswa__nama', 'program_mbkm__nama')
    list_filter = ('status_pendaftaran',)

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('nama', 'gasal_genap', 'tahun', 'aktif')
    search_fields = ('nama',)
    list_filter = ('gasal_genap', 'aktif')

@admin.register(Penyelia)
class PenyeliaAdmin(admin.ModelAdmin):
    list_display = ('nama', 'email', 'perusahaan')
    search_fields = ('nama', 'email')

@admin.register(Dosen)
class DosenAdmin(admin.ModelAdmin):
    list_display = ('nama', 'email', 'user')
    search_fields = ('nama', 'email')

@admin.register(PembimbingAkademik)
class PembimbingAkademikAdmin(admin.ModelAdmin):
    list_display = ('nama', 'email', 'user')
    search_fields = ('nama', 'email')

@admin.register(Manajemen)
class ManajemenFakultasAdmin(admin.ModelAdmin):
    list_display = ('nama', 'email', 'user')
    search_fields = ('nama', 'email')

@admin.register(PendaftaranKP)
class PendaftaranKPAdmin(admin.ModelAdmin):
    list_display = ('mahasiswa', 'semester', 'status_pendaftaran')
    search_fields = ('mahasiswa__nama', 'semester__nama')
    list_filter = ('status_pendaftaran',)

@admin.register(LaporanKP)
class LaporanKPAdmin(admin.ModelAdmin):
    list_display = ('pendaftaran', 'status', 'nilai', 'status_persetujuan_penyelia')
    search_fields = ('pendaftaran__mahasiswa__nama',)
    list_filter = ('status', 'status_persetujuan_penyelia')

@admin.register(LaporanMBKM)
class LaporanMBKMAdmin(admin.ModelAdmin):
    list_display = ('pendaftaran', 'status', 'sks_klaim', 'status_persetujuan_penyelia', 'status_persetujuan_dosen')
    search_fields = ('pendaftaran__mahasiswa__nama',)
    list_filter = ('status', 'status_persetujuan_penyelia', 'status_persetujuan_dosen')

@admin.register(LogMingguan)
class LogMingguanAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'pendaftaran_kp', 
        'pendaftaran_mbkm', 
        'tanggal_mulai', 
        'tanggal_selesai', 
        'status_persetujuan',
        'total_jam'
    )
    search_fields = (
        'pendaftaran_kp__mahasiswa__nama', 
        'pendaftaran_mbkm__mahasiswa__nama'
    )
    list_filter = ('tanggal_mulai', 'tanggal_selesai', 'status_persetujuan')

@admin.register(AktivitasHarian)
class AktivitasHarianAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'log_mingguan', 
        'tanggal', 
        'deskripsi', 
        'jam_mulai', 
        'jam_selesai', 
        'durasi',
    )
    search_fields = (
        'deskripsi', 
        'log_mingguan__pendaftaran_kp__mahasiswa__nama', 
        'log_mingguan__pendaftaran_mbkm__mahasiswa__nama'
    )
    list_filter = ('tanggal',)
