from django.test import TestCase
from PendaftaranMahasiswa.forms import PendaftaranMBKMForm
from PendaftaranMahasiswa.models import ProgramMBKM, Mahasiswa, Penyelia, Semester
from django.contrib.auth import get_user_model
import datetime

CustomUser = get_user_model()

class PendaftaranMBKMFormTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", password="password", email="test@example.com")
        self.semester = Semester.objects.create(semester="Gasal 2024", aktif=True, gasal_genap="Gasal")
        self.mahasiswa = Mahasiswa.objects.create(user=self.user, nama="Test Mahasiswa", npm="123456789")
        self.penyelia = Penyelia.objects.create(nama="Dosen PA", email="dosenpa@example.com", perusahaan="Universitas A")
        self.program = ProgramMBKM.objects.create(nama="Magang", minimum_sks=10, maksimum_sks=20)

    def test_form_valid(self):
        """ Test valid form submission """
        data = {
            "mahasiswa": self.mahasiswa.id,
            "semester": self.semester.id,
            "jumlah_semester": 5,
            "sks_diambil": 18,
            "program_mbkm": self.program.id,
            "penyelia": self.penyelia.id,
            "role": "Mahasiswa",
            "estimasi_sks_konversi": 15,
            "tanggal_mulai": datetime.date.today(),
            "pernyataan_komitmen": True,
            "status_pendaftaran": "Menunggu Persetujuan",
            "jenis_magang": ["studi_independent"],
        }
        form = PendaftaranMBKMForm(data)
        self.assertTrue(form.is_valid())

    def test_invalid_semester(self):
        """ Test mahasiswa semester kurang dari 5 tidak bisa mendaftar """
        data = {
            "mahasiswa": self.mahasiswa.id,
            "semester": self.semester.id,
            "jumlah_semester": 3,  # Semester kurang dari 5
            "sks_diambil": 18,
            "program_mbkm": self.program.id,
            "penyelia": self.penyelia.id,
            "role": "Mahasiswa",
            "estimasi_sks_konversi": 15,
            "tanggal_mulai": datetime.date.today(),
            "pernyataan_komitmen": True,
            "status_pendaftaran": "Menunggu Persetujuan",
            "jenis_magang": ["magang_mitra"],
        }
        form = PendaftaranMBKMForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("jumlah_semester", form.errors)

    def test_invalid_sks_konversi(self):
        """ Test SKS konversi tidak sesuai dengan batas program """
        data = {
            "mahasiswa": self.mahasiswa.id,
            "semester": self.semester.id,
            "jumlah_semester": 6,
            "sks_diambil": 18,
            "program_mbkm": self.program.id,
            "penyelia": self.penyelia.id,
            "role": "Mahasiswa",
            "estimasi_sks_konversi": 25,  # Melebihi maksimum 20 SKS
            "tanggal_mulai": datetime.date.today(),
            "pernyataan_komitmen": True,
            "status_pendaftaran": "Menunggu Persetujuan",
            "jenis_magang": ["magang_mandiri"],
        }
        form = PendaftaranMBKMForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("estimasi_sks_konversi", form.errors)

    def test_missing_komitmen(self):
        """ Test jika mahasiswa tidak menyetujui komitmen, form tidak valid """
        data = {
            "mahasiswa": self.mahasiswa.id,
            "semester": self.semester.id,
            "jumlah_semester": 5,
            "sks_diambil": 18,
            "program_mbkm": self.program.id,
            "penyelia": self.penyelia.id,
            "role": "Mahasiswa",
            "estimasi_sks_konversi": 15,
            "tanggal_mulai": datetime.date.today(),
            "pernyataan_komitmen": False,  # Komitmen tidak disetujui
            "status_pendaftaran": "Menunggu Persetujuan",
            "jenis_magang": ["studi_independent"],
        }
        form = PendaftaranMBKMForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("pernyataan_komitmen", form.errors)

    def test_form_dengan_data_kosong(self):
        """ Test form dengan semua field kosong """
        data = {}
        form = PendaftaranMBKMForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("mahasiswa", form.errors)
        self.assertIn("semester", form.errors)
        self.assertIn("sks_diambil", form.errors)
        self.assertIn("estimasi_sks_konversi", form.errors)
        self.assertIn("tanggal_mulai", form.errors)

    def test_invalid_jenis_magang(self):
        """ Test jika jenis magang kosong atau tidak valid """
        data = {
            "mahasiswa": self.mahasiswa.id,
            "semester": self.semester.id,
            "jumlah_semester": 6,
            "sks_diambil": 18,
            "program_mbkm": self.program.id,
            "penyelia": self.penyelia.id,
            "role": "Mahasiswa",
            "estimasi_sks_konversi": 15,
            "tanggal_mulai": datetime.date.today(),
            "pernyataan_komitmen": True,
            "status_pendaftaran": "Menunggu Persetujuan",
            "jenis_magang": [],
        }
        form = PendaftaranMBKMForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("jenis_magang", form.errors)

    def test_invalid_mahasiswa_not_exist(self):
        """ Test jika mahasiswa tidak ada dalam sistem """
        data = {
            "mahasiswa": 9999,  # ID Mahasiswa tidak ada
            "semester": self.semester.id,
            "jumlah_semester": 6,
            "sks_diambil": 18,
            "program_mbkm": self.program.id,
            "penyelia": self.penyelia.id,
            "role": "Mahasiswa",
            "estimasi_sks_konversi": 15,
            "tanggal_mulai": datetime.date.today(),
            "pernyataan_komitmen": True,
            "status_pendaftaran": "Menunggu Persetujuan",
            "jenis_magang": ["magang_mandiri"],
        }
        form = PendaftaranMBKMForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("mahasiswa", form.errors)

    def test_invalid_negative_sks_konversi(self):
        """ Test jika estimasi SKS konversi negatif atau nol tidak valid """
        data = {
            "mahasiswa": self.mahasiswa.id,
            "semester": self.semester.id,
            "jumlah_semester": 6,
            "sks_diambil": 18,
            "program_mbkm": self.program.id,
            "penyelia": self.penyelia.id,
            "role": "Mahasiswa",
            "estimasi_sks_konversi": -5,  # Nilai negatif
            "tanggal_mulai": datetime.date.today(),
            "pernyataan_komitmen": True,
            "status_pendaftaran": "Menunggu Persetujuan",
            "jenis_magang": ["magang_mandiri"],
        }
        form = PendaftaranMBKMForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("estimasi_sks_konversi", form.errors)