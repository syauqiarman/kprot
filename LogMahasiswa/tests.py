from django.http import JsonResponse
from django.test import TestCase, Client
from django.contrib.auth.models import User
from database.models import Mahasiswa, Penyelia, Semester, ProgramMBKM, PendaftaranMBKM, PendaftaranKP, LogMingguan, AktivitasHarian
from LogMahasiswa.forms import LogMingguanForm, AktivitasHarianFormSet
from datetime import date, timedelta
from django.urls import reverse
from django.core.exceptions import ValidationError

class BaseTest(TestCase):
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

class LogFormTest(BaseTest):
    def setUp(self):
        super().setUp()
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

    def test_valid_form(self):
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

    def test_invalid_program_type(self):
        """Test validasi dengan tipe program yang tidak valid"""
        # Buat program dengan tipe yang tidak valid tapi memiliki atribut yang diperlukan
        invalid_program = type('InvalidProgram', (), {
            'tanggal_mulai': date(2024, 7, 1),
            'tanggal_selesai': date(2024, 7, 31),
            'mahasiswa': self.mahasiswa,
            'penyelia': self.penyelia,
            'role': 'Test Role',
            'status_pendaftaran': 'Terdaftar'
        })()
        
        form_data = {
            'tanggal_mulai': '2024-07-01',
            'tanggal_selesai': '2024-07-07'
        }
        
        # Buat form dengan program yang tidak valid
        form = LogMingguanForm(program=invalid_program, data=form_data)
        
        # Cek bahwa form tidak valid
        self.assertFalse(form.is_valid())
        
        # Cek bahwa ValidationError muncul dengan pesan yang sesuai
        with self.assertRaisesMessage(ValidationError, "Jenis program tidak valid"):
            form._validate_overlap(
                tanggal_mulai=date(2024, 7, 1),
                tanggal_selesai=date(2024, 7, 7),
                program=invalid_program
            )

class LogViewsTest(BaseTest):
    def setUp(self):
        super().setUp()
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


## test delete log mahasiswa
    def test_create_log_POST_partial_week(self):
        """Bisa buat log mingguan meski tidak 7 hari penuh, asalkan tanggal valid dan aktivitas sesuai"""
        valid_data = {
            'tanggal_mulai': '2024-07-02',
            'tanggal_selesai': '2024-07-04',
            'aktivitas_harian-TOTAL_FORMS': '3',
            'aktivitas_harian-INITIAL_FORMS': '0',
        }
        for i in range(3):
            valid_data.update({
                f'aktivitas_harian-{i}-tanggal': f'2024-07-0{i+2}',
                f'aktivitas_harian-{i}-jam_mulai': '09:00',
                f'aktivitas_harian-{i}-jam_selesai': '15:00',
                f'aktivitas_harian-{i}-deskripsi': f'Aktivitas {i+1}',
            })

        self.client.force_login(self.user1)
        response = self.client.post(self.create_log_url, valid_data)

        self.assertRedirects(response, reverse('LogMahasiswa:log_detail'))
        self.assertEqual(LogMingguan.objects.count(), 1)
        self.assertEqual(AktivitasHarian.objects.count(), 3)

    def test_create_multiple_non_overlapping_logs(self):
        """Bisa membuat 2 log terpisah jika tidak tumpang tindih"""
        self.client.force_login(self.user1)

        for i in range(2):
            start_day = 2 + (i * 7)
            valid_data = {
                'tanggal_mulai': f'2024-07-{start_day:02}',
                'tanggal_selesai': f'2024-07-{start_day + 6:02}',
                'aktivitas_harian-TOTAL_FORMS': '2',
                'aktivitas_harian-INITIAL_FORMS': '0',
            }
            for j in range(2):
                valid_data.update({
                    f'aktivitas_harian-{j}-tanggal': f'2024-07-{start_day + j:02}',
                    f'aktivitas_harian-{j}-jam_mulai': '08:00',
                    f'aktivitas_harian-{j}-jam_selesai': '12:00',
                    f'aktivitas_harian-{j}-deskripsi': f'Aktivitas mingguan ke-{i+1}',
                })
            response = self.client.post(self.create_log_url, valid_data)
            self.assertEqual(response.status_code, 302)

        self.assertEqual(LogMingguan.objects.count(), 2)


    def test_create_log_invalid_jam_sama(self):
        """Jam mulai dan jam selesai sama harus dianggap invalid"""
        data = {
            'tanggal_mulai': '2024-07-02',
            'tanggal_selesai': '2024-07-08',
            'aktivitas_harian-TOTAL_FORMS': '1',
            'aktivitas_harian-INITIAL_FORMS': '0',
            'aktivitas_harian-0-tanggal': '2024-07-03',
            'aktivitas_harian-0-jam_mulai': '09:00',
            'aktivitas_harian-0-jam_selesai': '09:00',
            'aktivitas_harian-0-deskripsi': 'Aktivitas yang tidak valid',
        }
        self.client.force_login(self.user1)
        response = self.client.post(self.create_log_url, data)
        self.assertEqual(LogMingguan.objects.count(), 0)
        self.assertContains(response, "Jam mulai harus sebelum jam selesai")

    def test_create_log_invalid_dates_format(self):
        """Test kirim format tanggal tidak valid"""
        data = {
            'tanggal_mulai': '02-07-2024',  # Format tanggal tidak valid (seharusnya YYYY-MM-DD)
            'tanggal_selesai': '08-07-2024', # Format tanggal tidak valid (seharusnya YYYY-MM-DD)
            'aktivitas_harian-TOTAL_FORMS': '1',
            'aktivitas_harian-INITIAL_FORMS': '0',
            'aktivitas_harian-0-tanggal': '2024-07-03',
            'aktivitas_harian-0-jam_mulai': '08:00',
            'aktivitas_harian-0-jam_selesai': '17:00',
            'aktivitas_harian-0-deskripsi': 'Format salah',
        }
        
        self.client.force_login(self.user1)
        response = self.client.post(self.create_log_url, data)
        
        # Verifikasi bahwa form tidak valid
        self.assertEqual(response.status_code, 200)  # Tetap di halaman yang sama
        self.assertEqual(LogMingguan.objects.count(), 0)  # Tidak ada log yang dibuat

    def test_delete_log_success(self):
        """Test berhasil menghapus log"""
        # Create a log first
        log = LogMingguan.objects.create(
            pendaftaran_mbkm=self.pendaftaran_mbkm,
            tanggal_mulai=date(2024, 7, 2),
            tanggal_selesai=date(2024, 7, 8)
        )
        
        self.client.force_login(self.user1)
        response = self.client.post(reverse('LogMahasiswa:delete_log', args=[log.id]))
        
        # Check if redirect successful and log is deleted
        self.assertRedirects(response, reverse('LogMahasiswa:log_detail'))
        self.assertEqual(LogMingguan.objects.count(), 0)
        
    def test_delete_log_unauthorized(self):
        """Test gagal hapus log milik mahasiswa lain"""
        # Create another user and their program
        other_user = User.objects.create_user(username="otheruser", password="password")
        other_mahasiswa = Mahasiswa.objects.create(
            user=other_user, 
            nama="Other Student",
            email="other@example.com",
            npm="987654321",
            prodi="Ilmu Komputer"
        )
        other_pendaftaran = PendaftaranMBKM.objects.create(
            mahasiswa=other_mahasiswa,
            semester=self.semester_gasal,
            program_mbkm=self.program_mbkm,
            jumlah_semester=7,
            sks_diambil=12,
            penyelia=self.penyelia,
            role="Software Engineer",
            estimasi_sks_konversi=10,
            tanggal_mulai=date(2024, 7, 2),
            tanggal_selesai=date(2025, 1, 30),
            status_pendaftaran="Terdaftar",
            pernyataan_komitmen=True
        )
        
        # Create log for other user
        other_log = LogMingguan.objects.create(
            pendaftaran_mbkm=other_pendaftaran,
            tanggal_mulai=date(2024, 7, 2),
            tanggal_selesai=date(2024, 7, 8)
        )
        
        # Try to delete other user's log
        self.client.force_login(self.user1)
        response = self.client.post(reverse('LogMahasiswa:delete_log', args=[other_log.id]))
        
        # Check if deletion was prevented
        self.assertRedirects(response, reverse('LogMahasiswa:log_detail'))
        self.assertEqual(LogMingguan.objects.count(), 1)

    def test_delete_log_not_found(self):
        """Test hapus log yang tidak ada"""
        self.client.force_login(self.user1)
        response = self.client.post(reverse('LogMahasiswa:delete_log', args=[999]))
        
        self.assertEqual(response.status_code, 404)

    def test_create_log_no_activities(self):
        """Test create log tanpa aktivitas harian"""
        data = {
            'tanggal_mulai': '2024-07-02',
            'tanggal_selesai': '2024-07-08',
            'aktivitas_harian-TOTAL_FORMS': '1',
            'aktivitas_harian-INITIAL_FORMS': '0',
            'aktivitas_harian-0-DELETE': 'on'  # Mark the only activity for deletion
        }
        
        self.client.force_login(self.user1)
        response = self.client.post(self.create_log_url, data)
        
        self.assertEqual(response.status_code, 200)  # Stays on form
        self.assertEqual(LogMingguan.objects.count(), 0)
        self.assertContains(response, "Minimal harus ada satu aktivitas harian")

    def test_create_log_with_deleted_activities(self):
        """Test create log dengan beberapa aktivitas dihapus tapi masih ada yang valid"""
        data = {
            'tanggal_mulai': '2024-07-02',
            'tanggal_selesai': '2024-07-04',
            'aktivitas_harian-TOTAL_FORMS': '3',
            'aktivitas_harian-INITIAL_FORMS': '0',
        }
        
        # Add 3 activities but mark one for deletion
        for i in range(3):
            data.update({
                f'aktivitas_harian-{i}-tanggal': f'2024-07-0{i+2}',
                f'aktivitas_harian-{i}-jam_mulai': '09:00',
                f'aktivitas_harian-{i}-jam_selesai': '15:00',
                f'aktivitas_harian-{i}-deskripsi': f'Aktivitas {i+1}',
            })
        
        # Mark one activity for deletion
        data['aktivitas_harian-1-DELETE'] = 'on'
        
        self.client.force_login(self.user1)
        response = self.client.post(self.create_log_url, data)
        
        self.assertRedirects(response, reverse('LogMahasiswa:log_detail'))
        self.assertEqual(LogMingguan.objects.count(), 1)
        self.assertEqual(AktivitasHarian.objects.count(), 2)  # Only 2 activities should be saved

    def test_create_log_invalid_formset(self):
        """Test create log dengan formset tidak valid"""
        data = {
            'tanggal_mulai': '2024-07-02',
            'tanggal_selesai': '2024-07-04',
            'aktivitas_harian-TOTAL_FORMS': '1',
            'aktivitas_harian-INITIAL_FORMS': '0',
            'aktivitas_harian-0-tanggal': '2024-07-02',
            'aktivitas_harian-0-jam_mulai': '09:00',
            # Missing jam_selesai and deskripsi
        }
        
        self.client.force_login(self.user1)
        response = self.client.post(self.create_log_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(LogMingguan.objects.count(), 0)
        self.assertContains(response, "Terjadi kesalahan pada aktivitas harian")

    def test_create_log_ajax_success(self):
        """Test create log via AJAX request"""
        # Persiapkan data yang valid sesuai dengan periode program
        form_data = {
            'tanggal_mulai': self.pendaftaran_mbkm.tanggal_mulai.strftime('%Y-%m-%d'),
            'tanggal_selesai': (self.pendaftaran_mbkm.tanggal_mulai + timedelta(days=6)).strftime('%Y-%m-%d'),
            'aktivitas_harian-TOTAL_FORMS': '7',
            'aktivitas_harian-INITIAL_FORMS': '0',
            'aktivitas_harian-MIN_NUM_FORMS': '0',
            'aktivitas_harian-MAX_NUM_FORMS': '1000',
        }
        
        # Tambahkan data aktivitas harian untuk setiap hari
        for i in range(7):
            current_date = self.pendaftaran_mbkm.tanggal_mulai + timedelta(days=i)
            form_data.update({
                f'aktivitas_harian-{i}-tanggal': current_date.strftime('%Y-%m-%d'),
                f'aktivitas_harian-{i}-jam_mulai': '08:00',
                f'aktivitas_harian-{i}-jam_selesai': '16:00',
                f'aktivitas_harian-{i}-deskripsi': f'Aktivitas hari ke-{i+1}',
            })
        
        self.client.force_login(self.user1)
        response = self.client.post(
            self.create_log_url, 
            form_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(
            response.json()['redirect_url'], 
            reverse('LogMahasiswa:log_detail')
        )
        
        # Verifikasi log telah dibuat
        self.assertEqual(LogMingguan.objects.count(), 1)
        log = LogMingguan.objects.first()
        self.assertEqual(log.aktivitas_harian.count(), 7)
        self.assertEqual(
            log.tanggal_mulai,
            self.pendaftaran_mbkm.tanggal_mulai
        )

    def test_create_log_invalid_dates_format_ajax(self):
        """Test invalid date format via AJAX request"""
        invalid_data = {
            'tanggal_mulai': 'invalid-date',
            'tanggal_selesai': 'invalid-date',
            'aktivitas_harian-TOTAL_FORMS': '1',
            'aktivitas_harian-INITIAL_FORMS': '0',
        }
        
        self.client.force_login(self.user1)
        response = self.client.post(
            self.create_log_url, 
            invalid_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['success'])
        self.assertTrue('form_errors' in response.json())

    def test_create_log_invalid_formset_ajax(self):
        """Test invalid formset submission via AJAX request"""
        invalid_data = self.valid_data.copy()
        invalid_data['aktivitas_harian-0-jam_mulai'] = '10:00'
        invalid_data['aktivitas_harian-0-jam_selesai'] = '09:00'  # Invalid: end before start
        
        self.client.force_login(self.user1)
        response = self.client.post(
            self.create_log_url, 
            invalid_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['success'])
        self.assertTrue('formset_errors' in response.json())
        self.assertEqual(LogMingguan.objects.count(), 0)

    def test_process_dates_with_invalid_format(self):
        """Test _process_dates dengan format tanggal tidak valid"""
        from LogMahasiswa.views import _process_dates
        
        invalid_data = {
            'tanggal_mulai': 'invalid-date',
            'tanggal_selesai': 'invalid-date'
        }
        
        dates = _process_dates(invalid_data)
        self.assertEqual(dates, [])
    
    def test_handle_invalid_formset_errors_ajax(self):
        """Test handle invalid formset errors via AJAX request"""
        # Data formset dengan error (jam_selesai lebih awal dari jam_mulai)
        invalid_formset_data = {
            'aktivitas_harian-TOTAL_FORMS': '1',
            'aktivitas_harian-INITIAL_FORMS': '0',
            'aktivitas_harian-MIN_NUM_FORMS': '0',
            'aktivitas_harian-MAX_NUM_FORMS': '1000',
            'tanggal_mulai': '2024-07-01',
            'tanggal_selesai': '2024-07-07',
            'aktivitas_harian-0-tanggal': '2024-07-01',
            'aktivitas_harian-0-jam_mulai': '10:00',
            'aktivitas_harian-0-jam_selesai': '09:00',  # Error: jam selesai < jam mulai
            'aktivitas_harian-0-deskripsi': 'Test aktivitas'
        }

        self.client.force_login(self.user1)
        response = self.client.post(
            self.create_log_url,
            invalid_formset_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Verify response
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertFalse(response_data['success'])
        
        # Check formset_errors structure
        self.assertIn('formset_errors', response_data)
        self.assertIsInstance(response_data['formset_errors'], list)
        self.assertTrue(len(response_data['formset_errors']) > 0)
        
        # Check specific error in formset
        first_form_errors = response_data['formset_errors'][0]
        self.assertIn('jam_mulai', first_form_errors)
        self.assertEqual(
            first_form_errors['jam_mulai'][0],
            'Jam mulai harus sebelum jam selesai'
        )

        # Verify no activities were saved
        self.assertEqual(LogMingguan.objects.count(), 0)
        self.assertEqual(AktivitasHarian.objects.count(), 0)

    def test_handle_invalid_formset_direct(self):
        """Test fungsi _handle_invalid_formset secara langsung."""
        # Create a log instance
        log = LogMingguan.objects.create(
            pendaftaran_mbkm=self.pendaftaran_mbkm,
            tanggal_mulai='2024-07-01',
            tanggal_selesai='2024-07-07'
        )
        
        # Create invalid formset data 
        formset_data = {
            'aktivitas_harian-TOTAL_FORMS': '1',
            'aktivitas_harian-INITIAL_FORMS': '0',
            'aktivitas_harian-MIN_NUM_FORMS': '0',
            'aktivitas_harian-MAX_NUM_FORMS': '1000',
            'aktivitas_harian-0-tanggal': '2024-07-01',
            'aktivitas_harian-0-jam_mulai': '',  # Invalid: required field empty
            'aktivitas_harian-0-jam_selesai': '16:00',
            'aktivitas_harian-0-deskripsi': 'Test'
        }
        
        # Create formset with invalid data
        formset = AktivitasHarianFormSet(formset_data, instance=log)
        self.assertFalse(formset.is_valid())
        
        # Simulate AJAX request
        request = self.client.request().wsgi_request
        request.headers = {'X-Requested-With': 'XMLHttpRequest'}
        
        # Call function directly
        from LogMahasiswa.views import _handle_invalid_formset
        response = _handle_invalid_formset(request, formset, log)
        
        # Verify response
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        
        # Check response content - use response.content and json.loads()
        import json
        response_data = json.loads(response.content.decode('utf-8'))
        
        self.assertFalse(response_data['success'])
        self.assertIn('formset_errors', response_data)
        self.assertIsInstance(response_data['formset_errors'], list)
        
        # Verify specific error structure
        formset_errors = response_data['formset_errors']
        self.assertEqual(len(formset_errors), 1)  # Should have errors for one form
        self.assertIn('jam_mulai', formset_errors[0])  # Should have error for empty jam_mulai
        
        # Verify log deletion
        self.assertFalse(LogMingguan.objects.filter(id=log.id).exists())