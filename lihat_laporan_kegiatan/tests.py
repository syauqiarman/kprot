from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from input_detil.models import *
from datetime import date
from django.core.files.uploadedfile import SimpleUploadedFile

class LihatLaporanKegiatanTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

        # Create a user and penyelia
        cls.user1 = User.objects.create_user(username='penyelia_user', password='testpassword')
        cls.penyelia = Penyelia.objects.create(user=cls.user1, nama='Sutopo', email='sutopo@topo.id', perusahaan='Topo')

        # Create another user (not a penyelia)
        cls.user2 = User.objects.create_user(username='dosen_user', password='testpassword')
        cls.dosen = Dosen.objects.create(user=cls.user2, nama='Bambang', email='bambang@cs.edu')

        # Create Mahasiswa
        cls.user3 = User.objects.create_user(username='mahasiswa_user', password='testpassword')
        cls.mahasiswa = Mahasiswa.objects.create(user=cls.user3, nama='Joko', email='joko@depok.edu', npm='123456789')

        # Create Semester
        cls.semester = Semester.objects.create(
            nama="Gasal 24/25", gasal_genap="Gasal", tahun=2024, aktif=True
        )

        # Create ProgramMBKM
        cls.program_mbkm = ProgramMBKM.objects.create(
            nama="Studi Independent",
            minimum_sks=5,
            maksimum_sks=10
        )

        # Create PendaftaranKP and PendaftaranMBKM
        cls.pendaftaran_kp = PendaftaranKP.objects.create(
            mahasiswa=cls.mahasiswa,
            semester=cls.semester,
            jumlah_semester=7,
            sks_lulus=120,
            penyelia=cls.penyelia,
            role="Intern",
            total_jam_kerja=300,
            tanggal_mulai=date(2024, 6, 1),
            tanggal_selesai=date(2024, 9, 1),
            pernyataan_komitmen=True,
            status_pendaftaran="Terdaftar",
            history=["2024-03-08T12:34:56"],
        )

        cls.pendaftaran_mbkm = PendaftaranMBKM.objects.create(
            mahasiswa=cls.mahasiswa,
            semester=cls.semester,
            program_mbkm = cls.program_mbkm,
            jumlah_semester=5,
            penyelia=cls.penyelia,
            role="Intern",
            sks_diambil=10,
            estimasi_sks_konversi=5,
            tanggal_mulai=date(2024, 7, 1),
            tanggal_selesai=date(2024, 9, 1),
            pernyataan_komitmen=True,
            status_pendaftaran="Terdaftar",
            history=["2024-03-08T12:34:56"]
        )

        # Create Mock Reports
        cls.mock_file = SimpleUploadedFile("test.pdf", b"mock file content", content_type="application/pdf")

        cls.laporan_kp = LaporanKP.objects.create(
            pendaftaran=cls.pendaftaran_kp,
            file_laporan=cls.mock_file,
            file_timestamp=make_aware(datetime.now())
        )

        cls.laporan_mbkm = LaporanMBKM.objects.create(
            pendaftaran=cls.pendaftaran_mbkm,
            file_laporan=cls.mock_file,
            file_timestamp=make_aware(datetime.now()),
            sks_klaim=3
        )

    def test_unauthorized_access(self):
        """Test access by a user who is not a penyelia"""
        self.client.login(username='dosen_user', password='testpassword')
        response = self.client.get(reverse('lihat_laporan_kegiatan', args=[self.mahasiswa.id, 'kp']))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'error': 'Unauthorized'})

    def test_valid_kp_laporan(self):
        """Test fetching valid KP report"""
        self.client.login(username='penyelia_user', password='testpassword')
        response = self.client.get(reverse('lihat_laporan_kegiatan', args=[self.mahasiswa.id, 'kp']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lihat_laporan_kegiatan/lihat_laporan_kegiatan.html')
        self.assertEqual(response.context['id_mahasiswa'], self.mahasiswa.id)
        self.assertEqual(response.context['laporan'], LaporanKP.objects.filter(pendaftaran=self.pendaftaran_kp).first())

    def test_valid_mbkm_laporan(self):
        """Test fetching valid MBKM report"""
        self.client.login(username='penyelia_user', password='testpassword')
        response = self.client.get(reverse('lihat_laporan_kegiatan', args=[self.mahasiswa.id, 'mbkm']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lihat_laporan_kegiatan/lihat_laporan_kegiatan.html')
        self.assertEqual(response.context['id_mahasiswa'], self.mahasiswa.id)
        self.assertEqual(response.context['laporan'], LaporanMBKM.objects.filter(pendaftaran=self.pendaftaran_mbkm).first())

    def test_invalid_program(self):
        """Test invalid program input"""
        self.client.login(username='penyelia_user', password='testpassword')
        response = self.client.get(reverse('lihat_laporan_kegiatan', args=[self.mahasiswa.id, 'invalid_program']))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'error': 'Invalid program'})

    def test_mahasiswa_not_found(self):
        """Test when Mahasiswa does not exist"""
        self.client.login(username='penyelia_user', password='testpassword')
        response = self.client.get(reverse('lihat_laporan_kegiatan', args=[9999, 'kp']))
        self.assertEqual(response.status_code, 404)

    def test_pendaftaran_not_found(self):
        """Test when PendaftaranKP or PendaftaranMBKM does not exist"""
        self.pendaftaran_kp.delete()  # Ensure pendaftaran is removed
        self.client.login(username='penyelia_user', password='testpassword')
        response = self.client.get(reverse('lihat_laporan_kegiatan', args=[self.mahasiswa.id, 'kp']))
        self.assertEqual(response.status_code, 404)