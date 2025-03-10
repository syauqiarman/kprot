from datetime import date
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from .models import Mahasiswa, PendaftaranMBKM, Semester, ProgramMBKM
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
            'pernyataan_komitmen': True,
        }

    # Test case positif
    def test_form_fields_disabled(self):
        form = PendaftaranMBKMForm(user=self.user)
        self.assertTrue(form.fields['nama'].disabled)
        self.assertTrue(form.fields['npm'].disabled)
        self.assertTrue(form.fields['email'].disabled)

    def test_form_uses_mahasiswa_data(self):
        form = PendaftaranMBKMForm(user=self.user)
        self.assertEqual(form.fields['nama'].initial, self.mahasiswa.nama)
        self.assertEqual(form.fields['npm'].initial, self.mahasiswa.npm)
        self.assertEqual(form.fields['email'].initial, self.mahasiswa.email)

    def test_valid_form_without_file(self):
        form = PendaftaranMBKMForm(data=self.valid_data, user=self.user)
        self.assertTrue(form.is_valid())

    def test_valid_form_with_file(self):
        pdf_file = SimpleUploadedFile("test.pdf", b"file_content", content_type="application/pdf")
        form_data = self.valid_data.copy()
        form_data['tanggal_persetujuan'] = date.today()  # Tambahkan tanggal persetujuan
        form = PendaftaranMBKMForm(
            data=form_data, 
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

    def test_successful_registration_without_file(self):
        # Data valid tanpa file upload
        form_data = {
            'semester': self.semester.id,
            'jumlah_semester': 6,
            'sks_diambil': 10,
            'program_mbkm': self.program_mandiri.id,
            'estimasi_sks_konversi': 10,
            'rencana_lulus_semester_ini': False,
            'pernyataan_komitmen': True,  # Tambahkan pernyataan komitmen
        }

        # Submit form
        form = PendaftaranMBKMForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid(), form.errors)  # Pastikan form valid

        # Simpan data pendaftaran
        pendaftaran = form.save(commit=False)
        pendaftaran.mahasiswa = self.mahasiswa
        pendaftaran.save()

        # Verifikasi data tersimpan di database
        self.assertEqual(PendaftaranMBKM.objects.count(), 1)

        # Verifikasi status pendaftaran
        pendaftaran.refresh_from_db()
        self.assertEqual(pendaftaran.status_pendaftaran, "Menunggu Persetujuan PA")
        self.assertTrue(pendaftaran.pernyataan_komitmen)  # Pastikan pernyataan komitmen disetujui

    def test_missing_tanggal_persetujuan_with_file(self):
        # Data tidak valid: file diupload tapi tanggal_persetujuan tidak diisi
        pdf_file = SimpleUploadedFile("test.pdf", b"file_content", content_type="application/pdf")
        form = PendaftaranMBKMForm(
            data=self.valid_data, 
            files={'persetujuan_pa': pdf_file}, 
            user=self.user
        )
        self.assertFalse(form.is_valid())
        self.assertIn('tanggal_persetujuan', form.errors)
        self.assertEqual(
            form.errors['tanggal_persetujuan'][0],
            "Tanggal persetujuan harus diisi jika file persetujuan PA diupload."
        )
        

    def test_successful_registration_with_file(self):
        # Data valid dengan file upload
        form_data = {
            'semester': self.semester.id,
            'jumlah_semester': 6,
            'sks_diambil': 10,
            'program_mbkm': self.program_mandiri.id,
            'estimasi_sks_konversi': 10,
            'rencana_lulus_semester_ini': False,
            'pernyataan_komitmen': True,
            'tanggal_persetujuan': date.today(),  # Tambahkan tanggal persetujuan
        }
        pdf_file = SimpleUploadedFile("test.pdf", b"file_content", content_type="application/pdf")

        # Submit form dengan file
        form = PendaftaranMBKMForm(data=form_data, files={'persetujuan_pa': pdf_file}, user=self.user)
        self.assertTrue(form.is_valid(), form.errors)  # Pastikan form valid

        # Simpan data pendaftaran
        pendaftaran = form.save(commit=False)
        pendaftaran.mahasiswa = self.mahasiswa
        pendaftaran.save()

        # Verifikasi data tersimpan di database
        self.assertEqual(PendaftaranMBKM.objects.count(), 1)

        # Verifikasi status pendaftaran dan data lainnya
        pendaftaran.refresh_from_db()
        self.assertEqual(pendaftaran.status_pendaftaran, "Menunggu Verifikasi Dosen")
        self.assertIsNotNone(pendaftaran.persetujuan_pa)  # Pastikan file tersimpan
        self.assertIsNotNone(pendaftaran.tanggal_persetujuan)  # Pastikan tanggal persetujuan tersimpan
        self.assertTrue(pendaftaran.pernyataan_komitmen)  # Pastikan pernyataan komitmen disetujui

    def test_registration_with_invalid_semester(self):
        # Data tidak valid: jumlah semester kurang dari minimal
        invalid_data = {
            'semester': self.semester.id,
            'jumlah_semester': 4,  # Semester kurang dari minimal
            'sks_diambil': 10,
            'program_mbkm': self.program_mandiri.id,
            'estimasi_sks_konversi': 10,
            'rencana_lulus_semester_ini': False,
            'pernyataan_komitmen': True,
        }

        # Submit form
        form = PendaftaranMBKMForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('jumlah_semester', form.errors)

    def test_registration_with_invalid_sks_conversion(self):
        # Data tidak valid: estimasi SKS konversi melebihi batas
        invalid_data = {
            'semester': self.semester.id,
            'jumlah_semester': 6,
            'sks_diambil': 10,
            'program_mbkm': self.program_mandiri.id,
            'estimasi_sks_konversi': 25,  # SKS melebihi batas
            'rencana_lulus_semester_ini': False,
            'pernyataan_komitmen': True,
        }

        # Submit form
        form = PendaftaranMBKMForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('estimasi_sks_konversi', form.errors)

    def test_registration_with_total_sks_exceeding_limit(self):
        # Data tidak valid: total SKS melebihi 24
        invalid_data = {
            'semester': self.semester.id,
            'jumlah_semester': 6,
            'sks_diambil': 20,  # Total SKS = 30 (melebihi 24)
            'program_mbkm': self.program_mandiri.id,
            'estimasi_sks_konversi': 10,
            'rencana_lulus_semester_ini': False,
            'pernyataan_komitmen': True,
        }

        # Submit form
        form = PendaftaranMBKMForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('estimasi_sks_konversi', form.errors)

    def test_registration_without_commitment_statement(self):
        # Data tidak valid: pernyataan komitmen tidak disetujui
        invalid_data = {
            'semester': self.semester.id,
            'jumlah_semester': 6,
            'sks_diambil': 10,
            'program_mbkm': self.program_mandiri.id,
            'estimasi_sks_konversi': 10,
            'rencana_lulus_semester_ini': False,
            'pernyataan_komitmen': False,  # Pernyataan komitmen tidak disetujui
        }

        # Submit form
        form = PendaftaranMBKMForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('pernyataan_komitmen', form.errors)

    def test_registration_with_invalid_program(self):
        # Data tidak valid: program MBKM tidak valid
        invalid_data = {
            'semester': self.semester.id,
            'jumlah_semester': 6,
            'sks_diambil': 10,
            'program_mbkm': 999,  # Program MBKM tidak valid
            'estimasi_sks_konversi': 10,
            'rencana_lulus_semester_ini': False,
            'pernyataan_komitmen': True,
        }

        # Submit form
        form = PendaftaranMBKMForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('program_mbkm', form.errors)

    def test_form_uses_correct_mahasiswa_data(self):
        # Buat user dan mahasiswa
        user = User.objects.create_user(username="testuser2", password="password2")
        mahasiswa = Mahasiswa.objects.create(
            user=user, 
            nama="John Doe", 
            email="john@example.com", 
            npm="987654321"
        )

        # Inisialisasi form dengan user yang sedang login
        form = PendaftaranMBKMForm(user=user)

        # Verifikasi bahwa field nama, npm, dan email diisi dengan data mahasiswa
        self.assertEqual(form.fields['nama'].initial, mahasiswa.nama)
        self.assertEqual(form.fields['npm'].initial, mahasiswa.npm)
        self.assertEqual(form.fields['email'].initial, mahasiswa.email)

    def test_saved_pendaftaran_has_correct_mahasiswa_data(self):
        # Data valid untuk pendaftaran
        form_data = {
            'semester': self.semester.id,
            'jumlah_semester': 6,
            'sks_diambil': 10,
            'program_mbkm': self.program_mandiri.id,
            'estimasi_sks_konversi': 10,
            'rencana_lulus_semester_ini': False,
            'pernyataan_komitmen': True,
        }

        # Submit form
        form = PendaftaranMBKMForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid(), form.errors)

        # Simpan data pendaftaran
        pendaftaran = form.save(commit=False)
        pendaftaran.mahasiswa = self.mahasiswa
        pendaftaran.save()

        # Verifikasi bahwa data mahasiswa tersimpan dengan benar
        self.assertEqual(pendaftaran.mahasiswa.nama, self.mahasiswa.nama)
        self.assertEqual(pendaftaran.mahasiswa.npm, self.mahasiswa.npm)
        self.assertEqual(pendaftaran.mahasiswa.email, self.mahasiswa.email)