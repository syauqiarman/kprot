from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Mahasiswa)
class MahasiswaAdmin(admin.ModelAdmin):
    list_display = ('nama', 'npm', 'email', 'user')
    search_fields = ('nama', 'npm', 'email')
    list_filter = ('user',)

@admin.register(ProgramMBKM)
class ProgramMBKMAdmin(admin.ModelAdmin):
    list_display = ('nama', 'minimum_sks', 'maksimum_sks')
    search_fields = ('nama',)

@admin.register(PendaftaranMBKM)
class PendaftaranMBKMAdmin(admin.ModelAdmin):
    list_display = ('mahasiswa', 'program_mbkm', 'status_pendaftaran')
    search_fields = ('mahasiswanama', 'program_mbkmnama')
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

@admin.register(Kaprodi)
class KaprodiAdmin(admin.ModelAdmin):
    list_display = ('nama', 'email', 'user')
    search_fields = ('nama', 'email')

@admin.register(ManajemenFakultas)
class ManajemenFakultasAdmin(admin.ModelAdmin):
    list_display = ('nama', 'email', 'user')
    search_fields = ('nama', 'email')

@admin.register(PendaftaranKP)
class PendaftaranKPAdmin(admin.ModelAdmin):
    list_display = ('mahasiswa', 'semester', 'status_pendaftaran')
    search_fields = ('mahasiswa_nama', 'semester_nama')
    list_filter = ('status_pendaftaran',)

