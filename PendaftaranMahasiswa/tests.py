from django.test import TestCase
from PendaftaranMahasiswa.forms import PendaftaranMBKMForm
from PendaftaranMahasiswa.models import ProgramMBKM, Mahasiswa, Penyelia, Semester, User
from datetime import date

class PendaftaranMBKMFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.mahasiswa = Mahasiswa.objects.create(user=self.user, nama="Arthur", email="test1@example.com", npm="123456789")
        self.user2 = User.objects.create_user(username="testuser2", password="password2")
        self.penyelia = Penyelia.objects.create(user=self.user, nama="Agus", perusahaan="ABC", email="penyelia@company.com")
        self.semester = Semester.objects.create(nama="Gasal 24/25", gasal_genap="Gasal", tahun=2024, aktif=True)
        self.semester_genap = Semester.objects.create(nama="Genap 24/25", gasal_genap="Genap", tahun=2025, aktif=True)
        self.program = ProgramMBKM.objects.create(nama="Magang Mandiri", minimum_sks=10, maksimum_sks=20)

    def test_form_valid(self):
        """ Test valid form submission """
        data = {
            "mahasiswa": self.mahasiswa.id,
            "semester": self.semester.id,
            "jumlah_semester": 5,
            "sks_diambil": 18,
            "request_status_merdeka": False,
            "rencana_lulus_semester_ini": False,
            "program_mbkm": self.program.id,
            "penyelia": self.penyelia.id,
            "role": "Mahasiswa",
            "estimasi_sks_konversi": 15,
            "tanggal_mulai": date(2025, 1, 1),
            "tanggal_selesai": date(2025, 6, 1),
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
            "jumlah_semester": 3,
            "sks_diambil": 18,
            "request_status_merdeka": False,
            "rencana_lulus_semester_ini": False,
            "program_mbkm": self.program.id,
            "penyelia": self.penyelia.id,
            "role": "Mahasiswa",
            "estimasi_sks_konversi": 15,
            "tanggal_mulai": date(2025, 1, 1),
            "tanggal_selesai": date(2025, 6, 1),
            "pernyataan_komitmen": True,
            "status_pendaftaran": "Menunggu Persetujuan",
            "jenis_magang": ["studi_independent"],
        }
        form = PendaftaranMBKMForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("jumlah_semester", form.errors)

    def test_invalid_sks_konversi(self):
        """ Test SKS konversi tidak sesuai dengan batas program """
        data = {
            "mahasiswa": self.mahasiswa.id,
            "semester": self.semester.id,
            "jumlah_semester": 5,
            "sks_diambil": 18,
            "request_status_merdeka": False,
            "rencana_lulus_semester_ini": False,
            "program_mbkm": self.program.id,
            "penyelia": self.penyelia.id,
            "role": "Mahasiswa",
            "estimasi_sks_konversi": 25,
            "tanggal_mulai": date(2025, 1, 1),
            "tanggal_selesai": date(2025, 6, 1),
            "pernyataan_komitmen": True,
            "status_pendaftaran": "Menunggu Persetujuan",
            "jenis_magang": ["studi_independent"],
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
            "request_status_merdeka": False,
            "rencana_lulus_semester_ini": False,
            "program_mbkm": self.program.id,
            "penyelia": self.penyelia.id,
            "role": "Mahasiswa",
            "estimasi_sks_konversi": 15,
            "tanggal_mulai": date(2025, 1, 1),
            "tanggal_selesai": date(2025, 6, 1),
            "pernyataan_komitmen": False,
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
            "jumlah_semester": 5,
            "sks_diambil": 18,
            "request_status_merdeka": False,
            "rencana_lulus_semester_ini": False,
            "program_mbkm": self.program.id,
            "penyelia": self.penyelia.id,
            "role": "Mahasiswa",
            "estimasi_sks_konversi": 15,
            "tanggal_mulai": date(2025, 1, 1),
            "tanggal_selesai": date(2025, 6, 1),
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
            "mahasiswa": 9999,
            "semester": self.semester.id,
            "jumlah_semester": 5,
            "sks_diambil": 18,
            "request_status_merdeka": False,
            "rencana_lulus_semester_ini": False,
            "program_mbkm": self.program.id,
            "penyelia": self.penyelia.id,
            "role": "Mahasiswa",
            "estimasi_sks_konversi": 15,
            "tanggal_mulai": date(2025, 1, 1),
            "tanggal_selesai": date(2025, 6, 1),
            "pernyataan_komitmen": True,
            "status_pendaftaran": "Menunggu Persetujuan",
            "jenis_magang": ["studi_independent"],
        }
        form = PendaftaranMBKMForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("mahasiswa", form.errors)

    def test_invalid_negative_sks_konversi(self):
        """ Test jika estimasi SKS konversi negatif atau nol tidak valid """
        data = {
            "mahasiswa": self.mahasiswa.id,
            "semester": self.semester.id,
            "jumlah_semester": 5,
            "sks_diambil": 18,
            "request_status_merdeka": False,
            "rencana_lulus_semester_ini": False,
            "program_mbkm": self.program.id,
            "penyelia": self.penyelia.id,
            "role": "Mahasiswa",
            "estimasi_sks_konversi": -5,
            "tanggal_mulai": date(2025, 1, 1),
            "tanggal_selesai": date(2025, 6, 1),
            "pernyataan_komitmen": True,
            "status_pendaftaran": "Menunggu Persetujuan",
            "jenis_magang": ["studi_independent"],
        }
        form = PendaftaranMBKMForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("estimasi_sks_konversi", form.errors)