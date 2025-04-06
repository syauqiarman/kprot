from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from datetime import date, time

from database.models import AktivitasHarian, LogMingguan, PendaftaranKP, PendaftaranMBKM, Semester, ProgramMBKM, \
                            Mahasiswa, Penyelia, Kaprodi, PembimbingAkademik, Dosen, ManajemenFakultas

class ModelValidationTests(TestCase):
    @classmethod
    def setUp(cls):
        cls.user1 = User.objects.create_user(username="testuser1", password="password")
        cls.mahasiswa = Mahasiswa.objects.create(user=cls.user1, nama="Budi", email="test1@example.com", npm="123456789", prodi="Ilmu Komputer")
        cls.user2 = User.objects.create_user(username="testuser2", password="password")
        cls.penyelia = Penyelia.objects.create(user=cls.user2, nama="Siti", perusahaan="TechCorp", email="siti@company.com")
        cls.semester_gasal = Semester.objects.create(nama="Gasal 24/25", gasal_genap="Gasal", tahun=2024, aktif=True)
        cls.semester_genap = Semester.objects.create(nama="Genap 24/25", gasal_genap="Genap", tahun=2025, aktif=True)
        cls.program_mbkm = ProgramMBKM.objects.create(nama="Magang Mandiri", minimum_sks=10, maksimum_sks=20)

        cls.pendaftaran_kp = PendaftaranKP.objects.create(
            mahasiswa=cls.mahasiswa,
            semester=cls.semester_gasal,
            jumlah_semester=7,
            sks_lulus=120,
            penyelia=cls.penyelia,
            role="Software Engineer",
            total_jam_kerja=300,
            tanggal_mulai=date(2024, 4, 2),
            tanggal_selesai=date(2024, 10, 30),
            pernyataan_komitmen=True
        )

        cls.pendaftaran_mbkm = PendaftaranMBKM.objects.create(
            mahasiswa=cls.mahasiswa,
            semester=cls.semester_gasal,
            jumlah_semester=7,
            sks_diambil=12,
            rencana_lulus_semester_ini=False,
            program_mbkm=cls.program_mbkm,
            penyelia=cls.penyelia,
            role="Software Engineer",
            estimasi_sks_konversi=10,
            tanggal_mulai=date(2024, 7, 2),
            tanggal_selesai=date(2025, 1, 30),
            pernyataan_komitmen=True
        )

    def test_create_log_mingguan_with_kp(self):
        log = LogMingguan.objects.create(
            pendaftaran_kp=self.pendaftaran_kp,
            tanggal_mulai=date(2024, 4, 1),
            tanggal_selesai=date(2024, 4, 7)
        )
        self.assertEqual(log.program, self.pendaftaran_kp)
        self.assertEqual(log.status_persetujuan, 'pending')

    def test_create_log_mingguan_with_mbkm(self):
        log = LogMingguan.objects.create(
            pendaftaran_mbkm=self.pendaftaran_mbkm,
            tanggal_mulai=date(2024, 7, 1),
            tanggal_selesai=date(2024, 7, 7)
        )
        self.assertEqual(log.program, self.pendaftaran_mbkm)
        self.assertEqual(log.total_jam, 0.0)  # Default value

    def test_log_mingguan_constraint_violation(self):
        with self.assertRaises(Exception):
            LogMingguan.objects.create(
                pendaftaran_kp=self.pendaftaran_kp,
                pendaftaran_mbkm=self.pendaftaran_mbkm,
                tanggal_mulai=date(2024, 4, 1),
                tanggal_selesai=date(2024, 4, 7)
            )

    def test_calculate_total_jam(self):
        log = LogMingguan.objects.create(
            pendaftaran_kp=self.pendaftaran_kp,
            tanggal_mulai=date(2024, 4, 1),
            tanggal_selesai=date(2024, 4, 7)
        )
        
        # Create aktivitas harian
        AktivitasHarian.objects.create(
            log_mingguan=log,
            tanggal=date(2024, 4, 1),
            jam_mulai="09:00:00",
            jam_selesai="12:00:00",  # 3 jam
            deskripsi="Workshop"
        )
        
        AktivitasHarian.objects.create(
            log_mingguan=log,
            tanggal=date(2024, 4, 2),
            jam_mulai="13:00:00",
            jam_selesai="15:30:00",  # 2.5 jam
            deskripsi="Meeting"
        )

        total = 3 + 2.5
        self.assertEqual(log.calculate_total_jam(), total)

    def test_aktivitas_harian_durasi(self):
        log = LogMingguan.objects.create(
            pendaftaran_kp=self.pendaftaran_kp,
            tanggal_mulai=date(2024, 4, 1),
            tanggal_selesai=date(2024, 4, 7)
        )
        
        aktivitas = AktivitasHarian.objects.create(
            log_mingguan=log,
            tanggal=date(2024, 4, 3),
            jam_mulai=time(10, 0),        # 10:00:00 as time object
            jam_selesai=time(14, 30),     # 14:30:00 as time object
            deskripsi="Coding"
        )
        
        self.assertEqual(aktivitas.durasi, 4.5)