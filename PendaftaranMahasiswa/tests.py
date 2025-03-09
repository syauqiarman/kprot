from datetime import date
from django.test import TestCase
from PendaftaranMahasiswa.forms import PendaftaranKPForm
from PendaftaranMahasiswa.models import PendaftaranKP, Mahasiswa, Semester, User


class PendaftaranKPFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser1", password="password")
        cls.mahasiswa = Mahasiswa.objects.create(
            user=cls.user, nama="Budi", email="test1@example.com", npm="123456789"
        )

        cls.semester = Semester.objects.create(
            nama="Gasal 24/25", gasal_genap="Gasal", tahun=2024, aktif=True
        )

        cls.valid_data = {
            PendaftaranKP.objects.create(
                mahasiswa=cls.mahasiswa,
                semester=cls.semester,
                jumlah_semester=7,
                sks_lulus=120,
                pernyataan_komitmen=True,
                status_pendaftaran="Menunggu Detil",
                history=["2024-03-08T12:34:56"])
        }

        

    def test_form_valid(self):
        """Test kasus positif: Form valid dengan data yang benar"""
        form = PendaftaranKPForm(data=self.valid_data, mahasiswa=self.mahasiswa, semester=self.semester)
        self.assertTrue(form.is_valid())

    def test_form_invalid_jumlah_semester_too_low(self):
        """Test kasus negatif: jumlah_semester kurang dari batas minimum"""
        data = self.valid_data.copy()
        data["jumlah_semester"] = 5  # Batas minimum adalah 6
        form = PendaftaranKPForm(data=data, mahasiswa=self.mahasiswa, semester=self.semester)
        self.assertFalse(form.is_valid())
        self.assertIn("jumlah_semester", form.errors)

    def test_form_invalid_jumlah_semester_too_high(self):
        """Test kasus negatif: jumlah_semester lebih dari batas maksimum"""
        data = self.valid_data.copy()
        data["jumlah_semester"] = 13  # Batas maksimum adalah 12
        form = PendaftaranKPForm(data=data, mahasiswa=self.mahasiswa, semester=self.semester)
        self.assertFalse(form.is_valid())
        self.assertIn("jumlah_semester", form.errors)

    def test_form_invalid_sks_lulus_too_low(self):
        """Test kasus negatif: sks_lulus kurang dari batas minimum"""
        data = self.valid_data.copy()
        data["sks_lulus"] = 90  # Batas minimum adalah 100
        form = PendaftaranKPForm(data=data, mahasiswa=self.mahasiswa, semester=self.semester)
        self.assertFalse(form.is_valid())
        self.assertIn("sks_lulus", form.errors)

    def test_form_invalid_sks_lulus_too_high(self):
        """Test kasus negatif: sks_lulus lebih dari batas maksimum"""
        data = self.valid_data.copy()
        data["sks_lulus"] = 150  # Batas maksimum adalah 144
        form = PendaftaranKPForm(data=data, mahasiswa=self.mahasiswa, semester=self.semester)
        self.assertFalse(form.is_valid())
        self.assertIn("sks_lulus", form.errors)

    def test_form_invalid_pernyataan_komitmen_false(self):
        """Test kasus negatif: pernyataan komitmen tidak dicentang"""
        data = self.valid_data.copy()
        data["pernyataan_komitmen"] = False
        form = PendaftaranKPForm(data=data, mahasiswa=self.mahasiswa, semester=self.semester)
        self.assertFalse(form.is_valid())
        self.assertIn("pernyataan_komitmen", form.errors)

    def test_form_save_sets_status_pendaftaran(self):
        """Test: Menyimpan form harus menyetel status_pendaftaran"""
        form = PendaftaranKPForm(data=self.valid_data, mahasiswa=self.mahasiswa, semester=self.semester)
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(instance.status_pendaftaran, "Menunggu Detil")

    def test_form_clean_sets_status_pendaftaran(self):
        """Test: clean() harus menyetel status_pendaftaran"""
        form = PendaftaranKPForm(data=self.valid_data, mahasiswa=self.mahasiswa, semester=self.semester)
        form.is_valid()
        self.assertEqual(form.cleaned_data.get("status_pendaftaran", None), "Menunggu Detil")
