from django.test import TestCase, Client
from django.contrib.auth.models import User
from database.models import *
from LogMahasiswa.forms import LogMingguanForm, AktivitasHarianFormSet
from datetime import date
from django.urls import reverse

class LogFormTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", password="password")
        self.mahasiswa = Mahasiswa.objects.create(user=self.user1, nama="Budi", email="test1@example.com", npm="123456789", prodi="Ilmu Komputer")
        self.user2 = User.objects.create_user(username="testuser2", password="password")
        self.penyelia = Penyelia.objects.create(user=self.user2, nama="Siti", perusahaan="TechCorp", email="siti@company.com")
        self.semester_gasal = Semester.objects.create(nama="Gasal 24/25", gasal_genap="Gasal", tahun=2024, aktif=True)
        self.program_mbkm = ProgramMBKM.objects.create(nama="Magang Mandiri", minimum_sks=10, maksimum_sks=20)

        self.pendaftaran_mbkm = PendaftaranMBKM.objects.create(
            mahasiswa=self.mahasiswa,
            semester=self.semester_gasal,
            jumlah_semester=7,
            sks_diambil=12,
            rencana_lulus_semester_ini=False,
            program_mbkm=self.program_mbkm,
            penyelia=self.penyelia,
            role="Software Engineer",
            estimasi_sks_konversi=10,
            tanggal_mulai=date(2024, 7, 2),
            tanggal_selesai=date(2025, 1, 30),
            status_pendaftaran="Terdaftar",
            pernyataan_komitmen=True
        )

        self.pendaftaran_kp = PendaftaranKP.objects.create(
            mahasiswa=self.mahasiswa,
            semester=self.semester_gasal,
            jumlah_semester=7,
            sks_lulus=120,
            penyelia=self.penyelia,
            role="Software Engineer",
            total_jam_kerja=300,
            tanggal_mulai=date(2024, 4, 2),
            tanggal_selesai=date(2024, 10, 30),
            status_pendaftaran="Terdaftar",
            pernyataan_komitmen=True
        )

    def test_valid_form_mbkm(self):
        form_data = {
            'tanggal_mulai': '2024-07-02',
            'tanggal_selesai': '2024-07-08'
        }
        form = LogMingguanForm(program=self.pendaftaran_mbkm, data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_valid_form_kp(self):
        form_data = {
            'tanggal_mulai': '2024-07-02',
            'tanggal_selesai': '2024-07-08'
        }
        form = LogMingguanForm(program=self.pendaftaran_kp, data=form_data)
        self.assertTrue(form.is_valid())

    def test_save_with_new_instance_kp(self):
        """Test save untuk instance baru dengan program KP"""
        form_data = {
            'tanggal_mulai': '2024-07-02',
            'tanggal_selesai': '2024-07-08'
        }
        form = LogMingguanForm(program=self.pendaftaran_kp, data=form_data)
        if form.is_valid():
            log = form.save(commit=False)
            self.assertEqual(log.pendaftaran_kp, self.pendaftaran_kp)

    def test_form_save_with_kp(self):
        """Test save form dengan program KP"""
        form_data = {
            'tanggal_mulai': '2024-04-02',
            'tanggal_selesai': '2024-04-08'
        }
        form = LogMingguanForm(program=self.pendaftaran_kp, data=form_data)
        self.assertTrue(form.is_valid())
        
        log = form.save(commit=True)
        self.assertEqual(log.pendaftaran_kp, self.pendaftaran_kp)
        self.assertIsNotNone(log.pk)

    def test_form_update_excludes_self(self):
        """Test validasi overlap dengan exclude instance yang sedang diupdate"""
        log = LogMingguan.objects.create(
            pendaftaran_mbkm=self.pendaftaran_mbkm,
            tanggal_mulai='2024-07-02',
            tanggal_selesai='2024-07-08'
        )
        
        # Data update dengan tanggal sama
        form_data = {
            'tanggal_mulai': '2024-07-02',
            'tanggal_selesai': '2024-07-08'
        }
        form = LogMingguanForm(program=self.pendaftaran_mbkm, data=form_data, instance=log)
        self.assertTrue(form.is_valid())

    def test_invalid_date_range(self):
        form_data = {
            'tanggal_mulai': '2024-07-09',
            'tanggal_selesai': '2024-07-02'
        }
        form = LogMingguanForm(program=self.pendaftaran_mbkm, data=form_data)
        
        self.assertFalse(form.is_valid())
        # Periksa error spesifik di kedua field
        self.assertIn('tanggal_mulai', form.errors)
        self.assertIn('tanggal_selesai', form.errors)
        # Pastikan pesan error sesuai
        self.assertEqual(
            form.errors['tanggal_mulai'][0], 
            "Tanggal mulai tidak boleh setelah tanggal selesai"
        )

    def test_aktivitas_validation(self):
        log = LogMingguan.objects.create(
            pendaftaran_mbkm=self.pendaftaran_mbkm,
            tanggal_mulai='2024-07-02',
            tanggal_selesai='2024-07-09'
        )
        data = {
            'aktivitas_harian-TOTAL_FORMS': '1',
            'aktivitas_harian-INITIAL_FORMS': '0',
            'aktivitas_harian-0-tanggal': '2024-07-02',
            'aktivitas_harian-0-jam_mulai': '08:00',
            'aktivitas_harian-0-jam_selesai': '17:00',
            'aktivitas_harian-0-deskripsi': 'Test aktivitas'
        }
        formset = AktivitasHarianFormSet(data, instance=log)
        self.assertTrue(formset.is_valid())
    
    def test_valid_log_with_multiple_activities(self):
        log = LogMingguan.objects.create(
            pendaftaran_mbkm=self.pendaftaran_mbkm,
            tanggal_mulai='2024-07-02',
            tanggal_selesai='2024-07-08'
        )
        
        data = {
            'aktivitas_harian-TOTAL_FORMS': '3',
            'aktivitas_harian-INITIAL_FORMS': '0',
            'aktivitas_harian-0-tanggal': '2024-07-02',
            'aktivitas_harian-0-jam_mulai': '08:00',
            'aktivitas_harian-0-jam_selesai': '12:00',
            'aktivitas_harian-0-deskripsi': 'Membuat modul A',
            'aktivitas_harian-1-tanggal': '2024-07-03',
            'aktivitas_harian-1-jam_mulai': '09:00',
            'aktivitas_harian-1-jam_selesai': '17:00',
            'aktivitas_harian-1-deskripsi': 'Implementasi fitur X',
            'aktivitas_harian-2-tanggal': '2024-07-04',
            'aktivitas_harian-2-jam_mulai': '10:00',
            'aktivitas_harian-2-jam_selesai': '15:00',
            'aktivitas_harian-2-deskripsi': 'Bug fixing'
        }
        
        formset = AktivitasHarianFormSet(data, instance=log)
        self.assertTrue(formset.is_valid())

    def test_activity_outside_log_date_range(self):
        log = LogMingguan.objects.create(
            pendaftaran_mbkm=self.pendaftaran_mbkm,
            tanggal_mulai='2024-07-02',
            tanggal_selesai='2024-07-08'
        )
        
        data = {
            'aktivitas_harian-TOTAL_FORMS': '1',
            'aktivitas_harian-INITIAL_FORMS': '0',
            'aktivitas_harian-0-tanggal': '2024-07-09',  # Di luar range log
            'aktivitas_harian-0-jam_mulai': '08:00',
            'aktivitas_harian-0-jam_selesai': '17:00',
            'aktivitas_harian-0-deskripsi': 'Aktivitas invalid'
        }
        
        formset = AktivitasHarianFormSet(data, instance=log)
        self.assertFalse(formset.is_valid())
        self.assertIn('tanggal', formset.forms[0].errors)

    def test_overlapping_log_dates(self):
        # Log pertama yang valid
        LogMingguan.objects.create(
            pendaftaran_mbkm=self.pendaftaran_mbkm,
            tanggal_mulai='2024-07-02',
            tanggal_selesai='2024-07-08'
        )
        
        # Log kedua yang overlapping
        form_data = {
            'tanggal_mulai': '2024-07-05',
            'tanggal_selesai': '2024-07-12'
        }
        
        form = LogMingguanForm(program=self.pendaftaran_mbkm, data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_activity_time_range(self):
        log = LogMingguan.objects.create(
            pendaftaran_mbkm=self.pendaftaran_mbkm,
            tanggal_mulai='2024-07-02',
            tanggal_selesai='2024-07-08'
        )
        
        data = {
            'aktivitas_harian-TOTAL_FORMS': '1',
            'aktivitas_harian-INITIAL_FORMS': '0',
            'aktivitas_harian-0-tanggal': '2024-07-02',
            'aktivitas_harian-0-jam_mulai': '17:00',  # Waktu mulai > selesai
            'aktivitas_harian-0-jam_selesai': '08:00',
            'aktivitas_harian-0-deskripsi': 'Waktu invalid'
        }
        
        formset = AktivitasHarianFormSet(data, instance=log)
        self.assertFalse(formset.is_valid())
        self.assertIn('jam_mulai', formset.forms[0].errors)

    def test_empty_activity_description(self):
        log = LogMingguan.objects.create(
            pendaftaran_mbkm=self.pendaftaran_mbkm,
            tanggal_mulai='2024-07-02',
            tanggal_selesai='2024-07-08'
        )
        
        data = {
            'aktivitas_harian-TOTAL_FORMS': '1',
            'aktivitas_harian-INITIAL_FORMS': '0',
            'aktivitas_harian-0-tanggal': '2024-07-02',
            'aktivitas_harian-0-jam_mulai': '08:00',
            'aktivitas_harian-0-jam_selesai': '17:00',
            'aktivitas_harian-0-deskripsi': ''  # Deskripsi kosong
        }
        
        formset = AktivitasHarianFormSet(data, instance=log)
        self.assertFalse(formset.is_valid())
        self.assertIn('deskripsi', formset.forms[0].errors)

    def test_log_creation_without_program_approval(self):
        # Pastikan semua field required diisi
        pendaftaran_invalid = PendaftaranMBKM.objects.create(
            mahasiswa=self.mahasiswa,
            semester=self.semester_gasal,
            jumlah_semester=7,
            sks_diambil=12,
            program_mbkm=self.program_mbkm,
            penyelia=self.penyelia,
            role="Software Engineer",
            estimasi_sks_konversi=10,
            tanggal_mulai=date(2024, 7, 2),
            tanggal_selesai=date(2025, 1, 30),
            pernyataan_komitmen=True,
            status_pendaftaran="Menunggu Persetujuan PA"  # Status tidak memenuhi syarat
        )
        
        form_data = {
            'tanggal_mulai': '2024-07-02',
            'tanggal_selesai': '2024-07-08'
        }
        form = LogMingguanForm(program=pendaftaran_invalid, data=form_data)
        self.assertFalse(form.is_valid())
        
    def test_log_dates_outside_program_range(self):
        # Tanggal di luar range program MBKM
        form_data = {
            'tanggal_mulai': '2024-06-25',
            'tanggal_selesai': '2024-07-01'
        }
        
        form = LogMingguanForm(program=self.pendaftaran_mbkm, data=form_data)
        self.assertFalse(form.is_valid())

    def test_disabled_fields_content(self):
        form = LogMingguanForm(program=self.pendaftaran_mbkm)
        
        self.assertEqual(form.fields['nama'].initial, self.mahasiswa.nama)
        self.assertEqual(form.fields['npm'].initial, self.mahasiswa.npm)
        self.assertEqual(
            form.fields['tempat_magang'].initial, 
            self.penyelia.perusahaan
        )
        self.assertEqual(
            form.fields['role_magang'].initial, 
            self.pendaftaran_mbkm.role
        )

class LogViewsTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", password="password")
        self.mahasiswa = Mahasiswa.objects.create(user=self.user1, nama="Budi", email="test1@example.com", npm="123456789", prodi="Ilmu Komputer")
        self.user2 = User.objects.create_user(username="testuser2", password="password")
        self.penyelia = Penyelia.objects.create(user=self.user2, nama="Siti", perusahaan="TechCorp", email="siti@company.com")
        self.semester_gasal = Semester.objects.create(nama="Gasal 24/25", gasal_genap="Gasal", tahun=2024, aktif=True)
        self.program_mbkm = ProgramMBKM.objects.create(nama="Magang Mandiri", minimum_sks=10, maksimum_sks=20)

        self.pendaftaran_mbkm = PendaftaranMBKM.objects.create(
            mahasiswa=self.mahasiswa,
            semester=self.semester_gasal,
            jumlah_semester=7,
            sks_diambil=12,
            rencana_lulus_semester_ini=False,
            program_mbkm=self.program_mbkm,
            penyelia=self.penyelia,
            role="Software Engineer",
            estimasi_sks_konversi=10,
            tanggal_mulai=date(2024, 7, 2),
            tanggal_selesai=date(2025, 1, 31),
            status_pendaftaran="Terdaftar",
            pernyataan_komitmen=True
        )
        
        self.client = Client()
        self.create_log_url = reverse('LogMahasiswa:create_log')  # Sesuai app_name
        self.log_detail_url = reverse('LogMahasiswa:log_detail')
        
        self.valid_data = {
            'tanggal_mulai': '2024-07-01',
            'tanggal_selesai': '2024-07-07',
            'aktivitas_harian-TOTAL_FORMS': '7',
            'aktivitas_harian-INITIAL_FORMS': '0',
            'aktivitas_harian-MIN_NUM_FORMS': '0',
            'aktivitas_harian-MAX_NUM_FORMS': '1000',
        }
        
        for i in range(7):
            self.valid_data.update({
                f'aktivitas_harian-{i}-tanggal': f'2024-07-0{i+1}',
                f'aktivitas_harian-{i}-jam_mulai': '08:00',
                f'aktivitas_harian-{i}-jam_selesai': '16:00',
                f'aktivitas_harian-{i}-deskripsi': 'Bekerja pada modul X',
            })

    def test_create_log_GET_with_active_program(self):
        """Test GET request saat user memiliki program aktif"""
        self.client.force_login(self.user1)
        response = self.client.get(self.create_log_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_form.html')
        self.assertIsInstance(response.context['form'], LogMingguanForm)
        self.assertIsInstance(response.context['formset'], AktivitasHarianFormSet)

    def test_create_log_POST_valid_data(self):
        """Test POST dengan data valid membuat log baru"""
        valid_data = {
            'tanggal_mulai': '2024-07-02',
            'tanggal_selesai': '2024-07-08',
            'aktivitas_harian-TOTAL_FORMS': '7',
            'aktivitas_harian-INITIAL_FORMS': '0',
            'aktivitas_harian-MIN_NUM_FORMS': '0',
            'aktivitas_harian-MAX_NUM_FORMS': '1000',
        }
        for i in range(7):
            valid_data.update({
                f'aktivitas_harian-{i}-tanggal': f'2024-07-0{i+2}',
                f'aktivitas_harian-{i}-jam_mulai': '08:00',
                f'aktivitas_harian-{i}-jam_selesai': '16:00',
                f'aktivitas_harian-{i}-deskripsi': 'Bekerja pada modul X',
            })
        
        self.client.force_login(self.user1)
        response = self.client.post(self.create_log_url, valid_data)
        
        self.assertRedirects(response, reverse('LogMahasiswa:log_detail'))
        self.assertEqual(LogMingguan.objects.count(), 1)
        self.assertEqual(AktivitasHarian.objects.count(), 7)

    def test_create_log_with_kp_program(self):
        """Test membuat log dengan program KP"""
        # Hapus MBKM dan buat KP
        self.pendaftaran_mbkm.delete()
        pendaftaran_kp = PendaftaranKP.objects.create(
            mahasiswa=self.mahasiswa,
            semester=self.semester_gasal,
            jumlah_semester=7,
            sks_lulus=120,
            penyelia=self.penyelia,
            role="Developer",
            total_jam_kerja=300,
            tanggal_mulai=date(2024, 4, 1),
            tanggal_selesai=date(2024, 10, 30),
            status_pendaftaran="Terdaftar",
            pernyataan_komitmen=True
        )
        
        valid_data = {
            'tanggal_mulai': '2024-04-01',
            'tanggal_selesai': '2024-04-07',
            'aktivitas_harian-TOTAL_FORMS': '7',
            'aktivitas_harian-INITIAL_FORMS': '0',
        }
        
        for i in range(7):
            valid_data.update({
                f'aktivitas_harian-{i}-tanggal': f'2024-04-0{i+1}',
                f'aktivitas_harian-{i}-jam_mulai': '08:00',
                f'aktivitas_harian-{i}-jam_selesai': '16:00',
                f'aktivitas_harian-{i}-deskripsi': 'Bekerja pada modul Y',
            })
        
        self.client.force_login(self.user1)
        response = self.client.post(self.create_log_url, valid_data)
        
        self.assertRedirects(response, reverse('LogMahasiswa:log_detail'))
        self.assertEqual(LogMingguan.objects.count(), 1)
        log = LogMingguan.objects.first()
        self.assertEqual(log.pendaftaran_kp, pendaftaran_kp)

    def test_log_detail_with_kp_logs(self):
        """Test menampilkan log untuk program KP"""
        # Hapus MBKM dan buat KP
        self.pendaftaran_mbkm.delete()
        pendaftaran_kp = PendaftaranKP.objects.create(
            mahasiswa=self.mahasiswa,
            semester=self.semester_gasal,
            jumlah_semester=7,
            sks_lulus=120,
            penyelia=self.penyelia,
            role="Developer",
            total_jam_kerja=300,
            tanggal_mulai=date(2024, 4, 1),
            tanggal_selesai=date(2024, 10, 30),
            status_pendaftaran="Terdaftar",
            pernyataan_komitmen=True
        )
        
        # Buat log KP
        LogMingguan.objects.create(
            pendaftaran_kp=pendaftaran_kp,
            tanggal_mulai=date(2024, 4, 1),
            tanggal_selesai=date(2024, 4, 7),
            total_jam=40.0
        )
        
        self.client.force_login(self.user1)
        response = self.client.get(self.log_detail_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['logs']), 1)
        self.assertEqual(response.context['logs'][0].pendaftaran_kp, pendaftaran_kp)

    def test_create_log_POST_overlapping_dates(self):
        # Buat log pertama dengan tanggal valid dalam rentang program
        LogMingguan.objects.create(
            pendaftaran_mbkm=self.pendaftaran_mbkm,
            tanggal_mulai=date(2024, 7, 2),
            tanggal_selesai=date(2024, 7, 8),
            total_jam=20.0
        )
        
        # Data dengan tanggal yang tumpang tindih
        overlapping_data = {
            'tanggal_mulai': '2024-07-05',
            'tanggal_selesai': '2024-07-12',
            'aktivitas_harian-TOTAL_FORMS': '7',
            # ... (data aktivitas lainnya)
        }
        
        self.client.force_login(self.user1)
        response = self.client.post(self.create_log_url, overlapping_data)
        
        # Periksa pesan error
        self.assertFormError(response.context['form'], None, "Periode log ini tumpang tindih dengan log yang sudah ada")

    def test_create_log_POST_invalid_activity_time(self):
        """Test POST dengan jam mulai > jam selesai di aktivitas"""
        # Perbaiki tanggal log agar valid
        invalid_data = {
            'tanggal_mulai': '2024-07-02',
            'tanggal_selesai': '2024-07-08',
            'aktivitas_harian-TOTAL_FORMS': '1',
            'aktivitas_harian-INITIAL_FORMS': '0',
            'aktivitas_harian-0-tanggal': '2024-07-02',
            'aktivitas_harian-0-jam_mulai': '17:00',
            'aktivitas_harian-0-jam_selesai': '08:00',
            'aktivitas_harian-0-deskripsi': 'Waktu invalid'
        }
        
        self.client.force_login(self.user1)
        response = self.client.post(self.create_log_url, invalid_data)
        
        self.assertEqual(LogMingguan.objects.count(), 0)
        self.assertContains(response, "Jam mulai harus sebelum jam selesai")

    def test_log_detail_with_logs(self):
        # Buat log dengan total_jam yang valid
        LogMingguan.objects.create(
            pendaftaran_mbkm=self.pendaftaran_mbkm,
            tanggal_mulai=date(2024,7,2),
            tanggal_selesai=date(2024,7,8),
            total_jam=20.0
        )
        LogMingguan.objects.create(
            pendaftaran_mbkm=self.pendaftaran_mbkm,
            tanggal_mulai=date(2024,7,9),
            tanggal_selesai=date(2024,7,15),
            total_jam=15.5
        )
        
        self.client.force_login(self.user1)
        response = self.client.get(self.log_detail_url)
        
        # Pastikan context tersedia dan total_jam benar
        self.assertEqual(response.context['total_jam'], 35.5)

    def test_log_detail_without_logs(self):
        """Test halaman detail tanpa log"""
        self.client.force_login(self.user1)
        response = self.client.get(self.log_detail_url)
        
        self.assertContains(response, "Belum ada log mingguan yang tercatat.")
        self.assertEqual(response.context['total_jam'], 0.0)

    def test_access_without_active_program(self):
        self.pendaftaran_mbkm.delete()
        
        self.client.force_login(self.user1)
        response_create = self.client.get(self.create_log_url)
        response_detail = self.client.get(self.log_detail_url)
        
        # Perbaiki assertion dengan parameter fetch_redirect_response=False
        self.assertRedirects(response_create, '/', fetch_redirect_response=False)
        self.assertRedirects(response_detail, '/', fetch_redirect_response=False)