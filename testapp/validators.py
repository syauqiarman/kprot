from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import make_aware
from datetime import datetime, date
import re

# List of personal email domains to reject
PERSONAL_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com", "aol.com", "protonmail.com"
}

def validate_email_penyelia(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)$'
    if not re.fullmatch(pattern, email):
        raise ValidationError(_("Invalid email format."))

    domain = email.split('@')[-1].lower()
    if domain in PERSONAL_EMAIL_DOMAINS:
        raise ValidationError(_("Email pribadi tidak diperbolehkan. Gunakan email perusahaan atau institusi."))

def validate_jumlah_semester_kp(value):
    if not (6 <= value <= 12):
        raise ValidationError(_("Jumlah semester untuk mendaftar KP harus antara 6 hingga 12."))

def validate_sks_lulus(value):
    if not (100 <= value <= 144):
        raise ValidationError(_("Jumlah SKS lulus untuk mendaftar KP harus antara 100 hingga 144."))
    
def validate_total_jam_kerja(value):
    if not (280 <= value <= 400):
        raise ValidationError(_("Total jam kerja harus antara 280 hingga 400 jam."))
        
def validate_pernyataan_komitmen(value):
    if not value:
        raise ValidationError(_("Pernyataan komitmen harus disetujui."))

def validate_jumlah_semester_mbkm(value):
    if not (5 <= value <= 12):
        raise ValidationError(_("Jumlah semester untuk mendaftar MBKM harus antara 5 dan 12."))
    
def validate_sks_diambil(value):
    if value < 0:
        raise ValidationError(_("SKS yang diambil tidak boleh negatif."))
    
def validate_estimasi_sks_konversi(instance):
    if not hasattr(instance, 'program_mbkm') or instance.program_mbkm is None:
        raise ValidationError("Program MBKM harus dipilih.")
    
    if instance.estimasi_sks_konversi is None:
        return  # Skip validation if estimasi_sks_konversi is None
    
    min_sks = instance.program_mbkm.minimum_sks
    max_sks = instance.program_mbkm.maksimum_sks
    if not (min_sks <= instance.estimasi_sks_konversi <= max_sks):
        raise ValidationError(
            f"Estimasi SKS konversi untuk program {instance.program_mbkm.nama} harus antara {min_sks} dan {max_sks}."
        )
    
    if instance.sks_diambil is not None and instance.estimasi_sks_konversi + instance.sks_diambil > 24:
        raise ValidationError("Total SKS (sks_diambil + estimasi_sks_konversi) tidak boleh lebih dari 24.")
    
def determine_status_and_nilai_laporan_kp(instance):
    nilai_fields = [instance.nilai_abstrak, instance.nilai_isi, instance.nilai_lampiran, instance.nilai_konsistensi, instance.nilai_kerapihan]

    if all(n is not None for n in nilai_fields):
        if instance.nilai_abstrak < 3 or instance.nilai_isi < 3 or \
            instance.nilai_konsistensi < 4 or instance.nilai_lampiran < 4:
            instance.status = "Perlu Revisi"
        elif instance.nilai_kerapihan < 4:
            instance.status = "Sudah Dinilai Namun Belum Sesuai Format"
        else:
            instance.status = "Sudah Bisa Diberikan ke Perpustakaan"

        instance.nilai = (0.05 * instance.nilai_abstrak + 
                          0.7 * instance.nilai_isi + 
                          0.05 * instance.nilai_lampiran + 
                          0.1 * instance.nilai_konsistensi + 
                          0.1 * instance.nilai_kerapihan) * 25
    else:
        instance.status = "Belum Dinilai"

def validate_update_status_file_laporan_kp(instance, old_instance):
    if old_instance.file_laporan != instance.file_laporan:
        if instance.status != "Perlu Revisi":
            raise ValidationError(_("Mahasiswa tidak dapat mengunggah laporan baru jika statusnya bukan 'Perlu Revisi'."))

        instance.status = "Belum Dinilai"
        instance.status_persetujuan_penyelia = "-"
        instance.file_timestamp = make_aware(datetime.now()).isoformat()

def validate_nilai_changes_laporan_kp(instance, old_instance):
    nilai_changes = any([old_instance.nilai_abstrak != instance.nilai_abstrak, 
                         old_instance.nilai_isi != instance.nilai_isi, 
                         old_instance.nilai_lampiran != instance.nilai_lampiran, 
                         old_instance.nilai_konsistensi != instance.nilai_konsistensi, 
                         old_instance.nilai_kerapihan != instance.nilai_kerapihan])

    if instance.status_persetujuan_penyelia == "Ditolak" and nilai_changes:
        raise ValidationError(_("Dosen tidak dapat mengubah nilai jika laporan ditolak oleh penyelia."))
    
def validate_update_status_persetujuan_penyelia_laporan_kp(instance):
    if instance.status_persetujuan_penyelia == "Ditolak":
        if instance.feedback_penolakan_penyelia is None or instance.feedback_penolakan_penyelia == "":
            raise ValidationError(_("Feedback penolakan harus diisi."))
        instance.status = "Perlu Revisi"

def validate_update_status_file_laporan_mbkm(instance, old_instance):
    if old_instance.file_laporan != instance.file_laporan:
        if instance.status != "Perlu Revisi":
            raise ValidationError(_("Mahasiswa tidak dapat mengunggah laporan baru jika statusnya bukan 'Perlu Revisi'."))

        instance.status = "Belum Dicek"
        instance.status_persetujuan_penyelia = "-"
        instance.status_persetujuan_dosen = "-"
        instance.file_timestamp = make_aware(datetime.now()).isoformat()

def validate_update_status_persetujuan_penyelia_laporan_mbkm(instance):
    if instance.status_persetujuan_penyelia == "Ditolak":
        if instance.feedback_penolakan_penyelia is None or instance.feedback_penolakan_penyelia == "":
            raise ValidationError(_("Feedback penolakan harus diisi."))
        instance.status_persetujuan_dosen = "-"
        instance.status = "Perlu Revisi"

def validate_update_status_persetujuan_dosen_laporan_mbkm(instance):
    if instance.status_persetujuan_dosen == "Disetujui":
        instance.status = "Sudah Bisa Diberikan ke Perpustakaan"

    elif instance.status_persetujuan_dosen == "Ditolak":
        if instance.feedback_dosen is None or instance.feedback_dosen == "":
            raise ValidationError(_("Feedback penolakan harus diisi."))
        instance.status = "Perlu Revisi"

def validate_sks_klaim_laporan_mbkm(instance):
    if instance.sks_klaim is None or instance.pendaftaran is None or instance.pendaftaran.sks_diambil is None:
        return
        
    if instance.sks_klaim + instance.pendaftaran.sks_diambil > 24:
        raise ValidationError(_("Total SKS (sks_diambil + sks_klaim) tidak boleh lebih dari 24."))

    min_sks = instance.pendaftaran.program_mbkm.minimum_sks
    max_sks = instance.pendaftaran.program_mbkm.maksimum_sks
    if not (min_sks <= instance.sks_klaim <= max_sks):
        raise ValidationError(_(f"SKS klaim untuk program {instance.pendaftaran.program_mbkm.nama} harus antara {min_sks} dan {max_sks}."))