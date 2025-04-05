# tests/test_forms.py
from django.test import TestCase
from django.contrib.auth.models import User
from database.models import (
    Mahasiswa, Semester, PendaftaranKP, PendaftaranMBKM, 
    LogMingguan, AktivitasHarian
)
from LogMahasiswa.forms import LogMingguanForm, AktivitasHarianFormSet

class LogMingguanFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.mahasiswa = Mahasiswa.objects.create(
            user=self.user, 
            nama="John Doe",
            email="john@example.com",
            npm="12345678"
        )
        self.semester = Semester.objects.create(
            nama="2024 Gasal",
            gasal_genap="Gasal",
            tahun=2024,
            aktif=True
        )

    # Positive tests
    def test_valid_with_kp_registration(self):
        kp = PendaftaranKP.objects.create(
            mahasiswa=self.mahasiswa,
            semester=self.semester,
            jumlah_semester=5,
            sks_lulus=100,
            status_pendaftaran='Terdaftar'
        )
        
        form = LogMingguanForm({
            'tanggal_mulai': '2024-08-01',
            'tanggal_selesai': '2024-08-07'
        }, user=self.user)
        
        self.assertTrue(form.is_valid())
        log = form.save()
        self.assertEqual(log.pendaftaran_kp, kp)

    def test_valid_with_mbkm_registration(self):
        mbkm = PendaftaranMBKM.objects.create(
            mahasiswa=self.mahasiswa,
            semester=self.semester,
            jumlah_semester=5,
            status_pendaftaran='Terdaftar',
            program_mbkm_id=1  # Asumsi sudah ada program MBKM
        )
        
        form = LogMingguanForm({
            'tanggal_mulai': '2024-08-01',
            'tanggal_selesai': '2024-08-07'
        }, user=self.user)
        
        self.assertTrue(form.is_valid())
        log = form.save()
        self.assertEqual(log.pendaftaran_mbkm, mbkm)

    # Negative tests
    def test_no_active_registration(self):
        form = LogMingguanForm({
            'tanggal_mulai': '2024-08-01',
            'tanggal_selesai': '2024-08-07'
        }, user=self.user)
        
        self.assertFalse(form.is_valid())
        self.assertIn('Anda belum terdaftar', str(form.errors))

    def test_dates_overlap_existing_log(self):
        PendaftaranKP.objects.create(
            mahasiswa=self.mahasiswa,
            semester=self.semester,
            jumlah_semester=5,
            sks_lulus=100,
            status_pendaftaran='Terdaftar'
        )
        
        # Existing log
        LogMingguan.objects.create(
            pendaftaran_kp=self.mahasiswa.pendaftarankp_set.first(),
            tanggal_mulai='2024-08-01',
            tanggal_selesai='2024-08-07'
        )
        
        form = LogMingguanForm({
            'tanggal_mulai': '2024-08-05',
            'tanggal_selesai': '2024-08-10'
        }, user=self.user)
        
        self.assertFalse(form.is_valid())
        self.assertIn('tumpang tindih', str(form.errors))

class AktivitasHarianFormSetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.mahasiswa = Mahasiswa.objects.create(
            user=self.user, 
            nama="Arthur", 
            email="test1@example.com", 
            npm="123456789"
        )
        self.semester = Semester.objects.create(
            nama="Gasal 24/25", 
            gasal_genap="Gasal", 
            tahun=2024, 
            aktif=True
        )
        self.kp = PendaftaranKP.objects.create(
            mahasiswa=self.mahasiswa,
            semester=self.semester,
            jumlah_semester=5,
            sks_lulus=100,
            status_pendaftaran='Terdaftar'
        )
        self.log = LogMingguan.objects.create(
            pendaftaran_kp=self.kp,
            tanggal_mulai='2024-08-01',
            tanggal_selesai='2024-08-07'
        )

    # Positive test
    def test_valid_activity_entries(self):
        formset = AktivitasHarianFormSet(instance=self.log, data={
            'aktivitas_harian-TOTAL_FORMS': '2',
            'aktivitas_harian-INITIAL_FORMS': '0',
            'aktivitas_harian-0-tanggal': '2024-08-01',
            'aktivitas_harian-0-jam_mulai': '08:00',
            'aktivitas_harian-0-jam_selesai': '12:00',
            'aktivitas_harian-0-deskripsi': 'Activity 1',
            'aktivitas_harian-1-tanggal': '2024-08-02',
            'aktivitas_harian-1-jam_mulai': '09:00',
            'aktivitas_harian-1-jam_selesai': '11:00',
            'aktivitas_harian-1-deskripsi': 'Activity 2',
        })
        
        self.assertTrue(formset.is_valid())
        formset.save()
        self.assertEqual(self.log.aktivitas_harian.count(), 2)

    # Negative tests
    def test_invalid_time_range(self):
        formset = AktivitasHarianFormSet(instance=self.log, data={
            'aktivitas_harian-TOTAL_FORMS': '1',
            'aktivitas_harian-INITIAL_FORMS': '0',
            'aktivitas_harian-0-tanggal': '2024-08-01',
            'aktivitas_harian-0-jam_mulai': '12:00',
            'aktivitas_harian-0-jam_selesai': '08:00',  # Waktu mulai setelah selesai
            'aktivitas_harian-0-deskripsi': 'Invalid activity',
        })
        
        self.assertFalse(formset.is_valid())
        self.assertIn('Jam mulai harus', str(formset.errors))

    def test_activity_outside_log_period(self):
        formset = AktivitasHarianFormSet(instance=self.log, data={
            'aktivitas_harian-TOTAL_FORMS': '1',
            'aktivitas_harian-INITIAL_FORMS': '0',
            'aktivitas_harian-0-tanggal': '2024-07-30',  # Di luar range log
            'aktivitas_harian-0-jam_mulai': '08:00',
            'aktivitas_harian-0-jam_selesai': '12:00',
            'aktivitas_harian-0-deskripsi': 'Invalid date',
        })
        
        self.assertFalse(formset.is_valid())
        self.assertIn('harus dalam periode', str(formset.errors))

    def test_missing_required_fields(self):
        formset = AktivitasHarianFormSet(instance=self.log, data={
            'aktivitas_harian-TOTAL_FORMS': '1',
            'aktivitas_harian-INITIAL_FORMS': '0',
            'aktivitas_harian-0-tanggal': '',  # Tanggal kosong
            'aktivitas_harian-0-jam_mulai': '08:00',
            'aktivitas_harian-0-jam_selesai': '12:00',
            'aktivitas_harian-0-deskripsi': '',
        })
        
        self.assertFalse(formset.is_valid())
        self.assertIn('This field is required', str(formset.errors))