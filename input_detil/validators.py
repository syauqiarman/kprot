from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re
from datetime import date

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
    if value is None:
        return 
    
    if not (280 <= value <= 400):
        raise ValidationError(_("Total jam kerja harus antara 280 hingga 400 jam."))
        
def validate_pernyataan_komitmen(value):
    if not value:
        raise ValidationError(_("Pernyataan komitmen harus disetujui."))

def validate_jumlah_semester_mbkm(value):
    if not (5 <= value <= 12):
        raise ValidationError(_("Jumlah semester untuk mendaftar MBKM harus antara 5 dan 12."))
    
def validate_sks_diambil(value):
    if value is None:
        return
    if value < 0:
        raise ValidationError(_("SKS yang diambil tidak boleh negatif."))
    
def validate_estimasi_sks_konversi(instance):
    if instance.estimasi_sks_konversi is None:
        return # Skip validation if estimasi_sks_konversi is None
    
    min_sks = instance.program_mbkm.minimum_sks
    max_sks = instance.program_mbkm.maksimum_sks
    if not (min_sks <= instance.estimasi_sks_konversi <= max_sks):
        raise ValidationError(_(f"Estimasi SKS konversi untuk program {instance.program_mbkm.nama} harus antara {min_sks} dan {max_sks}."))
    if instance.estimasi_sks_konversi + instance.sks_diambil > 24:
        raise ValidationError(_("Total SKS (sks_diambil + estimasi_sks_konversi) tidak boleh lebih dari 24."))