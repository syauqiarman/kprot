from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from .models import Mahasiswa, Semester, ProgramMBKM
from .forms import PendaftaranMBKMForm

class PendaftaranMBKMFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.mahasiswa = Mahasiswa.objects.create(
            user=self.user, 
            nama="Arthur", 
            email="test1@example.com", 
            npm="123456789"
        )
        self.semester = Semester.objects.create(
            nama="Gasal 24/25", 
            gasal_genap="Gasal", 
            tahun=2024, 
            aktif=True
        )
        self.program_mandiri = ProgramMBKM.objects.create(
            nama="Magang Mandiri", 
            minimum_sks=10, 
            maksimum_sks=20
        )
        self.program_bumn = ProgramMBKM.objects.create(
            nama="Magang BUMN", 
            minimum_sks=10, 
            maksimum_sks=20
        )
        self.valid_data = {
            'semester': self.semester.id,
            'jumlah_semester': 6,
            'sks_diambil': 10,  # Diubah agar total SKS tidak melebihi 24
            'program_mbkm': self.program_mandiri.id,
            'estimasi_sks_konversi': 10,  # Diubah agar total SKS tidak melebihi 24
            'rencana_lulus_semester_ini': False,
        }

    # Test case positif
    def test_form_fields_disabled(self):
        form = PendaftaranMBKMForm(user=self.user)
        self.assertTrue(form.fields['nama'].disabled)
        self.assertTrue(form.fields['npm'].disabled)
        self.assertTrue(form.fields['email'].disabled)

    def test_valid_form_without_file(self):
        form = PendaftaranMBKMForm(data=self.valid_data, user=self.user)
        self.assertTrue(form.is_valid())

    def test_valid_form_with_file(self):
        pdf_file = SimpleUploadedFile("test.pdf", b"file_content", content_type="application/pdf")
        form = PendaftaranMBKMForm(
            data=self.valid_data, 
            files={'persetujuan_pa': pdf_file}, 
            user=self.user
        )
        self.assertTrue(form.is_valid())

    def test_valid_program_mbkm_choices(self):
        form = PendaftaranMBKMForm(user=self.user)
        programs = form.fields['program_mbkm'].queryset
        self.assertEqual(programs.count(), 2)
        self.assertIn(self.program_mandiri, programs)
        self.assertIn(self.program_bumn, programs)

    def test_valid_jumlah_semester(self):
        valid_data = self.valid_data.copy()
        valid_data['jumlah_semester'] = 6  # Semester valid
        form = PendaftaranMBKMForm(data=valid_data, user=self.user)
        self.assertTrue(form.is_valid())

    # Test case negatif
    def test_invalid_jumlah_semester(self):
        invalid_data = self.valid_data.copy()
        invalid_data['jumlah_semester'] = 4  # Semester kurang dari minimal
        form = PendaftaranMBKMForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('jumlah_semester', form.errors)
        self.assertEqual(
            form.errors['jumlah_semester'][0],
            "Minimal 5 semester untuk mendaftar program MBKM."
        )

    def test_missing_required_fields(self):
        required_fields = ['semester', 'jumlah_semester', 'program_mbkm']
        for field in required_fields:
            invalid_data = self.valid_data.copy()
            del invalid_data[field]
            form = PendaftaranMBKMForm(data=invalid_data, user=self.user)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)

    def test_invalid_sks_konversi(self):
        invalid_data = self.valid_data.copy()
        invalid_data['estimasi_sks_konversi'] = 25  # SKS melebihi maksimum
        form = PendaftaranMBKMForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('estimasi_sks_konversi', form.errors)
        self.assertEqual(
            form.errors['estimasi_sks_konversi'][0],
            "Estimasi SKS konversi untuk program Magang Mandiri harus antara 10 dan 20."
        )

    def test_total_sks_exceeds_limit(self):
        invalid_data = self.valid_data.copy()
        invalid_data['sks_diambil'] = 20
        invalid_data['estimasi_sks_konversi'] = 10  # Total SKS = 30 (melebihi 24)
        form = PendaftaranMBKMForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('estimasi_sks_konversi', form.errors)
        self.assertEqual(
            form.errors['estimasi_sks_konversi'][0],
            "Total SKS (sks_diambil + estimasi_sks_konversi) tidak boleh lebih dari 24."
        )

    def test_invalid_file_type(self):
        invalid_file = SimpleUploadedFile("test.txt", b"file_content", content_type="text/plain")
        form = PendaftaranMBKMForm(
            data=self.valid_data, 
            files={'persetujuan_pa': invalid_file}, 
            user=self.user
        )
        self.assertFalse(form.is_valid())
        self.assertIn('persetujuan_pa', form.errors)