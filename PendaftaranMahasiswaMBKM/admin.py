from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from database.models import Mahasiswa, ProgramMBKM, PendaftaranMBKM, Semester, Penyelia, Dosen, PembimbingAkademik, Kaprodi, ManajemenFakultas, PendaftaranKP, LogMingguan, AktivitasHarian

# Mendaftarkan semua model ke admin
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
    search_fields = ('mahasiswa__nama', 'program_mbkm__nama')
    list_filter = ('status_pendaftaran',)

@admin.register(PendaftaranKP)
class PendaftaranKPAdmin(admin.ModelAdmin):
    list_display = ('mahasiswa', 'status_pendaftaran')
    search_fields = ('mahasiswa__nama', 'status_pendaftaran')
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

class ProgramTypeFilter(SimpleListFilter):
    """Filter kustom untuk membedakan tipe program KP atau MBKM pada LogMingguan"""
    title = 'Tipe Program'
    parameter_name = 'program_type'

    def lookups(self, request, model_admin):
        return (
            ('kp', 'Kerja Praktek (KP)'),
            ('mbkm', 'MBKM'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'kp':
            return queryset.filter(pendaftaran_kp__isnull=False)
        elif self.value() == 'mbkm':
            return queryset.filter(pendaftaran_mbkm__isnull=False)
        return queryset

@admin.register(LogMingguan)
class LogMingguanAdmin(admin.ModelAdmin):
    list_display = ('get_program', 'tanggal_mulai', 'tanggal_selesai', 'status_persetujuan', 'total_jam')
    search_fields = (
        'pendaftaran_kp__mahasiswa__nama',
        'pendaftaran_mbkm__mahasiswa__nama',
        'status_persetujuan',
    )
    list_filter = (ProgramTypeFilter, 'status_persetujuan')

    def get_program(self, obj):
        """Menampilkan program terkait (KP atau MBKM)"""
        return obj.program
    get_program.short_description = 'Program Terkait'

@admin.register(AktivitasHarian)
class AktivitasHarianAdmin(admin.ModelAdmin):
    list_display = ('log_mingguan', 'tanggal', 'jam_mulai', 'jam_selesai', 'get_durasi', 'deskripsi')
    search_fields = (
        'deskripsi',
        'log_mingguan__pendaftaran_kp__mahasiswa__nama',
        'log_mingguan__pendaftaran_mbkm__mahasiswa__nama',
    )
    list_filter = ('tanggal',)

    def get_durasi(self, obj):
        """Menampilkan durasi dengan format angka 2 desimal"""
        return f"{obj.durasi:.2f} jam"
    get_durasi.short_description = 'Durasi'