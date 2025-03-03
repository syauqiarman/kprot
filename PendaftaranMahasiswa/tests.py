from datetime import date
from django.test import TestCase

from PendaftaranMahasiswa.forms import PendaftaranKPForm
from .models import *

# Create your tests here.

# TDD: Unit Test untuk PendaftaranKPForm
class PendaftaranKPFormTest(TestCase):
    def setUp(self):
        self.valid_data = {
            'jumlah_semester': 6,
            'sks_diambil': 120,
            'sks_lulus': 100,
            'role': 'Intern',
            'total_jam_kerja': 160,
            'tanggal_mulai': date.today(),
            'tanggal_selesai': date.today(),
            'pernyataan_komitmen': True,
            'status_pendaftaran': 'Menunggu Persetujuan'
        }
    
    def test_valid_form(self):
        form = PendaftaranKPForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_invalid_sks_lulus(self):
        data = self.valid_data.copy()
        data['sks_lulus'] = 90
        form = PendaftaranKPForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("Anda tidak memenuhi syarat karena SKS Lulus kurang dari 100.", str(form.errors))
    
    def test_invalid_semester(self):
        data = self.valid_data.copy()
        data['jumlah_semester'] = 5
        form = PendaftaranKPForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("Anda tidak memenuhi syarat karena Semester kurang dari 6.", str(form.errors))
    
    def test_pernyataan_komitmen_required(self):
        data = self.valid_data.copy()
        data['pernyataan_komitmen'] = False
        form = PendaftaranKPForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("Anda harus menyetujui pernyataan komitmen.", str(form.errors))
