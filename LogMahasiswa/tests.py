from django.test import TestCase
from django.contrib.auth.models import User
from database.models import *
from LogMahasiswa.forms import *
import datetime

class LogFormTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", password="password")
        self.mahasiswa = Mahasiswa.objects.create(user=self.user1, nama="Budi", email="test1@example.com", npm="123456789")
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

    def test_valid_form(self):
        form_data = {
            'tanggal_mulai': '2024-07-02',
            'tanggal_selesai': '2024-07-09'
        }
        form = LogMingguanForm(program=self.pendaftaran_mbkm, data=form_data)
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