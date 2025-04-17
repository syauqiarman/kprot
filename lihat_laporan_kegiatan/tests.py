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
            sks_klaim=7
        )

    def test_unauthorized_access(self):
        """Test access by a user who is not a penyelia"""
        self.client.login(username='dosen_user', password='testpassword')
        response = self.client.get(reverse('lihat_laporan_kegiatan:lihat_laporan_kegiatan', args=['kp', self.mahasiswa.id, self.pendaftaran_kp.id]))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'error': 'Unauthorized'})

    def test_invalid_program(self):
        """Test invalid program input"""
        self.client.login(username='penyelia_user', password='testpassword')
        response = self.client.get(reverse('lihat_laporan_kegiatan:lihat_laporan_kegiatan', args=['invalid_program', self.mahasiswa.id, self.pendaftaran_kp.id]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'error': 'Invalid program'})

    def test_mahasiswa_not_found(self):
        """Test when Mahasiswa does not exist"""
        self.client.login(username='penyelia_user', password='testpassword')
        response = self.client.get(reverse(
            'lihat_laporan_kegiatan:lihat_laporan_kegiatan',
            args=['kp', 9999, self.pendaftaran_kp.id]
        ))
        self.assertEqual(response.status_code, 404)

    def test_pendaftaran_not_found(self):
        """Test when PendaftaranKP or PendaftaranMBKM does not exist"""
        self.client.login(username='penyelia_user', password='testpassword')
        invalid_pendaftaran_id = 9999  # ID yang tidak ada
        response = self.client.get(reverse('lihat_laporan_kegiatan:lihat_laporan_kegiatan', args=['kp', self.mahasiswa.id, invalid_pendaftaran_id]))
        self.assertEqual(response.status_code, 404)

    def test_authorized_access_kp(self):
        """Test authorized access for KP reports"""
        self.client.login(username='penyelia_user', password='testpassword')
        response = self.client.get(reverse(
            'lihat_laporan_kegiatan:lihat_laporan_kegiatan',
            args=['kp', self.mahasiswa.id, self.pendaftaran_kp.id]
        ))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.mahasiswa.nama)
        self.assertContains(response, self.pendaftaran_kp.role)

    def test_authorized_access_mbkm(self):
        """Test authorized access for MBKM reports"""
        self.client.login(username='penyelia_user', password='testpassword')
        response = self.client.get(reverse(
            'lihat_laporan_kegiatan:lihat_laporan_kegiatan',
            args=['mbkm', self.mahasiswa.id, self.pendaftaran_mbkm.id]
        ))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.mahasiswa.nama)
        self.assertContains(response, self.pendaftaran_mbkm.role)

    def test_laporan_not_found(self):
        """Test when Laporan does not exist"""
        self.laporan_kp.delete()  # Remove the KP report
        self.client.login(username='penyelia_user', password='testpassword')
        response = self.client.get(reverse(
            'lihat_laporan_kegiatan:lihat_laporan_kegiatan',
            args=['kp', self.mahasiswa.id, self.pendaftaran_kp.id]
        ))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Belum ada laporan yang dikirim.")

    def test_approve_laporan_kp(self):
        """Test approving a KP report"""
        self.client.login(username='penyelia_user', password='testpassword')
        response = self.client.post(
            reverse('lihat_laporan_kegiatan:persetujuan_laporan', args=['kp', self.mahasiswa.id]),
            {'action': 'approve'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.laporan_kp.refresh_from_db()
        self.assertEqual(self.laporan_kp.status_persetujuan_penyelia, 'Disetujui')
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Laporan disetujui.')

    def test_reject_laporan_mbkm(self):
        """Test rejecting a MBKM report with feedback"""
        self.client.login(username='penyelia_user', password='testpassword')
        feedback = "Laporan perlu perbaikan pada bagian metodologi."
        response = self.client.post(
            reverse('lihat_laporan_kegiatan:persetujuan_laporan', args=['mbkm', self.mahasiswa.id]),
            {'action': 'reject', 'feedback': feedback},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.laporan_mbkm.refresh_from_db()
        self.assertEqual(self.laporan_mbkm.status_persetujuan_penyelia, 'Ditolak')
        self.assertEqual(self.laporan_mbkm.feedback_penolakan_penyelia, feedback)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Laporan ditolak dengan feedback.')

    def test_reject_laporan_without_feedback(self):
        """Test rejecting a report without feedback should fail"""
        self.client.login(username='penyelia_user', password='testpassword')
        response = self.client.post(
            reverse('lihat_laporan_kegiatan:persetujuan_laporan', args=['kp', self.mahasiswa.id]),
            {'action': 'reject', 'feedback': ''},
            follow=True,
            **{'HTTP_REFERER': reverse('lihat_laporan_kegiatan:temp_dashboard_penyelia')}
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Feedback harus diisi saat menolak laporan.')
        self.laporan_kp.refresh_from_db()
        self.assertNotEqual(self.laporan_kp.status_persetujuan_penyelia, 'Ditolak')

    def test_invalid_action(self):
        """Test submitting an invalid action"""
        self.client.login(username='penyelia_user', password='testpassword')
        response = self.client.post(
            reverse('lihat_laporan_kegiatan:persetujuan_laporan', args=['kp', self.mahasiswa.id]),
            {'action': 'invalid_action'},
            follow=True,
            **{'HTTP_REFERER': reverse('lihat_laporan_kegiatan:temp_dashboard_penyelia')}
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Aksi tidak valid.')

    def test_temp_dashboard_penyelia_access(self):
        """Test access to penyelia dashboard"""
        self.client.login(username='penyelia_user', password='testpassword')
        response = self.client.get(reverse('lihat_laporan_kegiatan:temp_dashboard_penyelia'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.mahasiswa.nama)

    def test_temp_dashboard_unauthorized_access(self):
        """Test unauthorized access to penyelia dashboard"""
        self.client.login(username='dosen_user', password='testpassword')
        response = self.client.get(reverse('lihat_laporan_kegiatan:temp_dashboard_penyelia'))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'error': 'Unauthorized'})

    def test_valid_kp_laporan(self):
        """Test fetching valid KP report"""
        self.client.login(username='penyelia_user', password='testpassword')
        response = self.client.get(reverse(
            'lihat_laporan_kegiatan:lihat_laporan_kegiatan',
            args=['kp', self.mahasiswa.id, self.pendaftaran_kp.id]
        ))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lihat_laporan_kegiatan.html')
        self.assertEqual(
            response.context['laporan'],
            LaporanKP.objects.filter(pendaftaran=self.pendaftaran_kp).first()
        )

    def test_valid_mbkm_laporan(self):
        """Test fetching valid MBKM report"""
        self.client.login(username='penyelia_user', password='testpassword')
        response = self.client.get(reverse(
            'lihat_laporan_kegiatan:lihat_laporan_kegiatan',
            args=['mbkm', self.mahasiswa.id, self.pendaftaran_mbkm.id]
        ))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lihat_laporan_kegiatan.html')
        self.assertEqual(
            response.context['laporan'],
            LaporanMBKM.objects.filter(pendaftaran=self.pendaftaran_mbkm).first()
        )