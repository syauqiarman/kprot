from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from database.models import Aktivitas, Hari, LogMingguan, Mahasiswa, ProgramMBKM, PendaftaranMBKM, Semester, Penyelia, Dosen, PembimbingAkademik, Kaprodi, ManajemenFakultas, PendaftaranKP

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

class AktivitasInline(admin.TabularInline):
    model = Aktivitas
    extra = 1
    fields = ('jam_mulai', 'jam_selesai', 'deskripsi', 'durasi')
    readonly_fields = ('durasi',)
    
    def durasi(self, instance):
        return f"{instance.durasi:.2f} Jam"

class HariInline(admin.TabularInline):
    model = Hari
    extra = 1
    fields = ('tanggal', 'total_jam_hari')
    readonly_fields = ('total_jam_hari',)
    inlines = [AktivitasInline]
    
    def total_jam_hari(self, instance):
        return f"{sum(a.durasi for a in instance.aktivitas.all()):.2f} Jam"
    total_jam_hari.short_description = "Total Jam"

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
    list_display = ('periode', 'program_info', 'total_jam', 'status_persetujuan')
    list_filter = (ProgramTypeFilter, 'status_persetujuan', 'tanggal_mulai')
    search_fields = (
        'pendaftaran_kp__mahasiswa__nama',
        'pendaftaran_mbkm__mahasiswa__nama'
    )
    inlines = [HariInline]
    
    fieldsets = (
        (None, {
            'fields': (
                ('pendaftaran_kp', 'pendaftaran_mbkm'),
                ('tanggal_mulai', 'tanggal_selesai'),
                'status_persetujuan',
                'alasan_penolakan'
            )
        }),
    )
    
    def periode(self, obj):
        return f"{obj.tanggal_mulai} - {obj.tanggal_selesai}"
    
    def program_info(self, obj):
        if obj.pendaftaran_kp:
            return f"KP: {obj.pendaftaran_kp.mahasiswa.nama}"
        return f"MBKM: {obj.pendaftaran_mbkm.mahasiswa.nama}"
    program_info.short_description = 'Program'

@admin.register(Hari)
class HariAdmin(admin.ModelAdmin):
    list_display = ('tanggal', 'log_mingguan_link', 'total_jam')
    list_filter = ('log_mingguan__pendaftaran_kp', 'log_mingguan__pendaftaran_mbkm')
    inlines = [AktivitasInline]
    
    def log_mingguan_link(self, obj):
        return f"Log {obj.log_mingguan.tanggal_mulai} - {obj.log_mingguan.tanggal_selesai}"
    log_mingguan_link.short_description = 'Log Mingguan'
    
    def total_jam(self, obj):
        return f"{sum(a.durasi for a in obj.aktivitas.all()):.2f} Jam"

@admin.register(Aktivitas)
class AktivitasAdmin(admin.ModelAdmin):
    list_display = ('hari_info', 'jam_mulai', 'jam_selesai', 'durasi', 'deskripsi_pendek')
    list_filter = ('hari__log_mingguan__pendaftaran_kp', 'hari__log_mingguan__pendaftaran_mbkm')
    
    def hari_info(self, obj):
        return f"{obj.hari.tanggal} ({obj.hari.log_mingguan})"
    hari_info.short_description = 'Hari'
    
    def durasi(self, obj):
        return f"{obj.durasi:.2f} Jam"
    
    def deskripsi_pendek(self, obj):
        return obj.deskripsi[:50] + '...' if len(obj.deskripsi) > 50 else obj.deskripsi
    deskripsi_pendek.short_description = 'Deskripsi'