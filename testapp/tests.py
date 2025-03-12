from django.test import TestCase
from django.urls import reverse
from testapp.models import *
from django.contrib.auth.models import User

class MahasiswaFilterTests(TestCase):
    def setUp(self):
        """Setup data awal untuk pengujian"""
         # Buat user untuk masing-masing mahasiswa
        self.user_20 = User.objects.create_user(username='mahasiswa20', password='password123')
        self.user_21 = User.objects.create_user(username='mahasiswa21', password='password123')
        self.user_22 = User.objects.create_user(username='mahasiswa22', password='password123')
        self.user_penyelia = User.objects.create_user(username="penyelia", password="password")
        self.user_pa = User.objects.create_user(username="pa_user", password="password")

        # Buat semester
        self.semester_2025 = Semester.objects.create(nama="Gasal 2025", gasal_genap="Gasal", tahun=2025, aktif=False)
        self.semester_2026 = Semester.objects.create(nama="Genap 2026", gasal_genap="Genap", tahun=2026, aktif=False)
        self.semester_2027 = Semester.objects.create(nama="Gasal 2027", gasal_genap="Gasal", tahun=2027, aktif=True)

        self.pa = PembimbingAkademik.objects.create(user=self.user_pa, nama="PAK", email="test5@example.com")
        self.penyelia = Penyelia.objects.create(user=self.user_penyelia, nama="Siti", perusahaan="TechCorp", email="siti@company.com")
        self.program_mbkm = ProgramMBKM.objects.create(nama="Magang Mandiri", minimum_sks=10, maksimum_sks=20)

        # Buat mahasiswa dengan angkatan berbeda
        self.mahasiswa_20 = Mahasiswa.objects.create(
            user=self.user_20, nama="Andi", npm="200123456", email="andi@example.com", pa=self.pa
        )
        self.mahasiswa_21 = Mahasiswa.objects.create(
            user=self.user_21, nama="Budi", npm="210123456", email="budi@example.com", pa=self.pa
        )
        self.mahasiswa_22 = Mahasiswa.objects.create(
            user=self.user_22, nama="Caca", npm="220123456", email="caca@example.com", pa=self.pa
        )
        
        # Buat data PendaftaranKP dan PendaftaranMBKM untuk mahasiswa di semester berbeda
        self.pendaftaran_kp1 = PendaftaranKP.objects.create(
            mahasiswa=self.mahasiswa_20,
            semester=self.semester_2026,
            jumlah_semester=7,
            sks_lulus=120,  
            penyelia=self.penyelia,
            role="Software Engineer",
            total_jam_kerja=300,
            tanggal_mulai=date(2025, 10, 2),
            tanggal_selesai=date(2026, 4, 29),
            pernyataan_komitmen=True
        )
        
        self.pendaftaran_kp2 = PendaftaranKP.objects.create(
            mahasiswa=self.mahasiswa_21,
            semester=self.semester_2027,
            jumlah_semester=7,
            sks_lulus=120,
            penyelia=self.penyelia,
            role="Software Engineer",
            total_jam_kerja=300,
            tanggal_mulai=date(2027, 4, 2),
            tanggal_selesai=date(2027, 10, 30),
            pernyataan_komitmen=True
        )

        self.pendaftaran_mbkm1 = PendaftaranMBKM.objects.create(
            mahasiswa=self.mahasiswa_22,
            semester=self.semester_2027,
            jumlah_semester=7,
            sks_diambil=12,
            rencana_lulus_semester_ini=False,
            program_mbkm=self.program_mbkm, 
            penyelia=self.penyelia,
            role="Software Engineer",
            estimasi_sks_konversi=10,
            tanggal_mulai=date(2027, 7, 2),
            tanggal_selesai=date(2028, 1, 30),
            pernyataan_komitmen=True
        )

    def test_filter_by_semester(self):
        """Pastikan hanya mahasiswa yang terdaftar di semester yang dipilih muncul"""
        response = self.client.get(reverse('testapp:list_mahasiswa', args=[self.semester_2027.id]))
        self.assertContains(response, "Budi")  # Mahasiswa 21 (KP, semester 2027)
        self.assertContains(response, "Caca")  # Mahasiswa 22 (MBKM, semester 2027)
        self.assertNotContains(response, "Andi")  # Mahasiswa 20 tidak terdaftar di semester 2027

    def test_filter_by_angkatan(self):
        """Pastikan hanya mahasiswa dari angkatan tertentu yang muncul"""
        response = self.client.get(reverse('testapp:list_mahasiswa', args=[self.semester_2027.id]) + "?angkatan=21")
        self.assertContains(response, "Budi")  # Mahasiswa 21 harus muncul
        self.assertNotContains(response, "Caca")  # Mahasiswa 22 harus tersembunyi
        self.assertNotContains(response, "Andi")  # Mahasiswa 20 harus tersembunyi

    def test_filter_by_program_kp(self):
        """Pastikan hanya mahasiswa yang terdaftar di KP yang muncul"""
        response = self.client.get(reverse('testapp:list_mahasiswa', args=[self.semester_2027.id]) + "?program=KP")
        self.assertContains(response, "Budi")  # Mahasiswa 21 ada di KP
        self.assertNotContains(response, "Caca")  # Mahasiswa 22 ada di MBKM, harus tersembunyi

    def test_filter_by_program_mbkm(self):
        """Pastikan hanya mahasiswa yang terdaftar di MBKM yang muncul"""
        response = self.client.get(reverse('testapp:list_mahasiswa', args=[self.semester_2027.id]) + "?program=MBKM")
        self.assertContains(response, "Caca")  # Mahasiswa 22 ada di MBKM
        self.assertNotContains(response, "Budi")  # Mahasiswa 21 ada di KP, harus tersembunyi

    def test_filter_no_result(self):
        """Pastikan ketika filter yang diberikan tidak cocok, hasilnya kosong"""
        response = self.client.get(reverse('testapp:list_mahasiswa', args=[self.semester_2027.id]) + "?angkatan=20")
        self.assertNotContains(response, "Budi")
        self.assertNotContains(response, "Caca")
        self.assertNotContains(response, "Andi")  # Harus kosong karena angkatan 20 tidak ada di semester 2027

    def test_filter_by_status_positive(self):
        """Pastikan mahasiswa dengan status tertentu muncul"""
        # Atur status pendaftaran untuk KP dan MBKM
        self.pendaftaran_kp2.status_pendaftaran = "Terdaftar"
        self.pendaftaran_kp2.save()
        self.pendaftaran_mbkm1.status_pendaftaran = "Menunggu Persetujuan PA"
        self.pendaftaran_mbkm1.save()

        # Filter untuk mahasiswa dengan status "Terdaftar" (KP)
        response_kp = self.client.get(reverse('testapp:list_mahasiswa', args=[self.semester_2027.id]) + "?status=Terdaftar")
        self.assertContains(response_kp, "Budi")  # Mahasiswa 21 dengan KP "Terdaftar"
        self.assertNotContains(response_kp, "Caca")  # Mahasiswa 22 tidak boleh muncul

        # Filter untuk mahasiswa dengan status "Menunggu Persetujuan PA" (MBKM)
        response_mbkm = self.client.get(reverse('testapp:list_mahasiswa', args=[self.semester_2027.id]) + "?status=Menunggu%20Persetujuan%20PA")
        self.assertContains(response_mbkm, "Caca")  # Mahasiswa 22 dengan MBKM "Menunggu Persetujuan PA"
        self.assertNotContains(response_mbkm, "Budi")  # Mahasiswa 21 tidak boleh muncul

    def test_filter_by_status_negative(self):
        """Pastikan mahasiswa dengan status yang tidak sesuai tidak muncul"""
        # Atur status pendaftaran untuk KP dan MBKM
        self.pendaftaran_kp2.status_pendaftaran = "Terdaftar"
        self.pendaftaran_kp2.save()
        self.pendaftaran_mbkm1.status_pendaftaran = "Menunggu Persetujuan PA"
        self.pendaftaran_mbkm1.save()

        # Filter untuk status yang tidak ada ("Ditolak Kaprodi")
        response = self.client.get(reverse('testapp:list_mahasiswa', args=[self.semester_2027.id]) + "?status=Ditolak%20Kaprodi")
        self.assertNotContains(response, "Budi")  # Mahasiswa 21 tidak boleh muncul
        self.assertNotContains(response, "Caca")  # Mahasiswa 22 tidak boleh muncul
        self.assertContains(response, "Tidak ada mahasiswa yang sesuai dengan filter")  # Pastikan pesan kosong muncul

    def test_list_semester(self):
        """Pastikan halaman daftar semester menampilkan semua semester yang ada"""
        response = self.client.get(reverse('testapp:list_semester'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gasal 2025")
        self.assertContains(response, "Genap 2026")
        self.assertContains(response, "Gasal 2027")