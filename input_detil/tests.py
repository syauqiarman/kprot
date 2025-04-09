from django.test import TestCase, Client
from input_detil.models import Mahasiswa, Penyelia, User, Semester, PendaftaranKP, Dosen
from input_detil.services import PendaftaranKPService
from input_detil.forms import InputDetilKPForm
from datetime import date
from django.urls import reverse

class InputDetilKPTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test user and mahasiswa
        cls.user1 = User.objects.create_user(username="testuser1", email="test1@example.com", password="password")
        cls.mahasiswa1 = Mahasiswa.objects.create(
            user=cls.user1, nama="Budi", email="test1@example.com", npm="123456789", prodi="Ilmu Komputer"
        )

        # Create test semester
        cls.semester = Semester.objects.create(
            nama="Gasal 24/25", gasal_genap="Gasal", tahun=2024, aktif=True
        )

        # Create test penyelia
        cls.user9 = User.objects.create_user(username="testuser9", password="password")
        cls.penyelia = Penyelia.objects.create(user=cls.user9, nama="Siti", perusahaan="TechCorp", email="siti@company.com")

        # Create test PendaftaranKP instance
        cls.pendaftaran_kp = PendaftaranKP.objects.create(
            mahasiswa=cls.mahasiswa1,
            semester=cls.semester,
            jumlah_semester=7,
            sks_lulus=120,
            penyelia=cls.penyelia,
            role="Intern",
            total_jam_kerja=300,
            tanggal_mulai=date(2024, 6, 1),
            tanggal_selesai=date(2024, 9, 1),
            pernyataan_komitmen=True,
            status_pendaftaran="Menunggu Detil",
            history=["2024-03-08T12:34:56"],
        )

        cls.client = Client()
    
    def setUp(self):
        self.client.login(username="testuser1", password="password")

    def test_form_prefills_static_student_data(self):
        """Test that the form prefills readonly fields with student data."""
        form = InputDetilKPForm(instance=self.pendaftaran_kp)
        self.assertEqual(form.fields["mahasiswa"].initial, "Budi")
        self.assertEqual(form.fields["npm"].initial, "123456789")
        self.assertEqual(form.fields["prodi"].initial, "Ilmu Komputer")
        self.assertEqual(form.fields["semester"].initial, "Gasal 24/25")
        self.assertEqual(form.fields["sks_lulus"].initial, 120)

    def test_readonly_fields_cannot_be_changed(self):
        """Test that readonly fields are not included in cleaned_data."""
        form = InputDetilKPForm(
            data={
                "role": "Intern",
                "total_jam_kerja": 300,
                "tanggal_mulai": "2024-06-01",
                "tanggal_selesai": "2024-09-01",
                "penyelia_nama": "Dr. Supervisor",
                "penyelia_perusahaan": "PT AI Research",
                "penyelia_email": "supervisor@example.com",
            },
            instance=self.pendaftaran_kp,
        )
        self.assertTrue(form.is_valid())  # Ensure form is valid for other fields
        self.assertNotIn("mahasiswa", form.cleaned_data)
        self.assertNotIn("npm", form.cleaned_data)
        self.assertNotIn("prodi", form.cleaned_data)
        self.assertNotIn("semester", form.cleaned_data)
        self.assertNotIn("sks_lulus", form.cleaned_data)

    def test_invalid_end_date_before_start_date(self):
        """Test validation for end date before start date."""
        form = InputDetilKPForm(
            data={
                "role": "Intern",
                "total_jam_kerja": 160,
                "tanggal_mulai": "2024-09-01",
                "tanggal_selesai": "2024-06-01",
                "penyelia_nama": "Dr. Supervisor",
                "penyelia_perusahaan": "PT AI Research",
                "penyelia_email": "supervisor@example.com",
            },
            instance=self.pendaftaran_kp,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("tanggal_selesai", form.errors)

    def test_invalid_negative_working_hours(self):
        """Test validation for negative working hours."""
        form = InputDetilKPForm(
            data={
                "role": "Intern",
                "total_jam_kerja": -5,
                "tanggal_mulai": "2024-06-01",
                "tanggal_selesai": "2024-09-01",
                "penyelia_nama": "Dr. Supervisor",
                "penyelia_perusahaan": "PT AI Research",
                "penyelia_email": "supervisor@example.com",
            },
            instance=self.pendaftaran_kp,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("total_jam_kerja", form.errors)

    def test_form_invalid_without_required_fields(self):
        """Test that the form is invalid when required fields are missing."""
        form = InputDetilKPForm(data={}, instance=self.pendaftaran_kp)
        self.assertFalse(form.is_valid())

        expected_errors = [
            "role", "total_jam_kerja", "tanggal_mulai", "tanggal_selesai",
            "penyelia_nama", "penyelia_perusahaan", "penyelia_email"
        ]
        for field in expected_errors:
            self.assertIn(field, form.errors)

    def test_service_get_pending_registration(self):
        """Test that the service retrieves the correct pending registration."""
        registration = PendaftaranKPService.get_pending_registration(self.user1)
        self.assertEqual(registration, self.pendaftaran_kp)
        self.assertEqual(registration.status_pendaftaran, "Menunggu Detil")

    def test_service_check_has_pending_registration(self):
        """Test that the service correctly checks for pending registrations."""
        self.assertTrue(PendaftaranKPService.check_has_pending_registration(self.pendaftaran_kp))

        inactive_semester = Semester.objects.create(nama="Gasal 23/24", gasal_genap="Gasal", tahun=2023, aktif=False)
        inactive_pendaftaran = PendaftaranKP.objects.create(
            mahasiswa=self.mahasiswa1,
            semester=inactive_semester,
            jumlah_semester=7,
            sks_lulus=120,
            penyelia=self.penyelia,
            role="Intern",
            total_jam_kerja=300,
            tanggal_mulai=date(2023, 6, 1),
            tanggal_selesai=date(2023, 9, 1),
            pernyataan_komitmen=True,
            status_pendaftaran='Terdaftar',
            history=["2024-03-08T12:34:56"],
        )
        self.assertFalse(PendaftaranKPService.check_has_pending_registration(inactive_pendaftaran))

    def test_post_simpan_detil_kp_creates_new_penyelia(self):
        """Test POST to simpan_detil_kp creates a new penyelia."""
        url = reverse('input_detil:simpan_detil_kp', args=[self.pendaftaran_kp.id])
        response = self.client.post(url, {
            "role": "Intern",
            "total_jam_kerja": 300,
            "tanggal_mulai": "2024-06-01",
            "tanggal_selesai": "2024-09-01",
            "penyelia_nama": "New Supervisor",
            "penyelia_perusahaan": "New Company",
            "penyelia_email": "new.supervisor@example.com",
        })
        self.assertRedirects(response, reverse("input_detil:input_detil_success", args=[self.pendaftaran_kp.id]))

        updated = PendaftaranKP.objects.get(id=self.pendaftaran_kp.id)
        self.assertEqual(updated.penyelia.nama, "New Supervisor")
        self.assertEqual(updated.status_pendaftaran, "Terdaftar")

    def test_post_reuses_existing_penyelia(self):
        """Test POST reuses existing penyelia instead of creating a new one."""
        url = reverse('input_detil:simpan_detil_kp', args=[self.pendaftaran_kp.id])
        response = self.client.post(url, {
            "role": "Intern",
            "total_jam_kerja": 300,
            "tanggal_mulai": "2024-06-01",
            "tanggal_selesai": "2024-09-01",
            "penyelia_nama": "Siti",
            "penyelia_perusahaan": "TechCorp",
            "penyelia_email": "siti@company.com",
        })
        self.assertRedirects(response, reverse("input_detil:input_detil_success", args=[self.pendaftaran_kp.id]))

        updated = PendaftaranKP.objects.get(id=self.pendaftaran_kp.id)
        self.assertEqual(updated.penyelia.id, self.penyelia.id)

    def test_post_invalid_dates_shows_errors(self):
        """Test POST with invalid date range returns to form with errors."""
        url = reverse('input_detil:simpan_detil_kp', args=[self.pendaftaran_kp.id])
        response = self.client.post(url, {
            "role": "Intern",
            "total_jam_kerja": 300,
            "tanggal_mulai": "2024-09-01",
            "tanggal_selesai": "2024-06-01",  # Invalid
            "penyelia_nama": "Siti",
            "penyelia_perusahaan": "TechCorp",
            "penyelia_email": "siti@company.com",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tanggal selesai harus setelah tanggal mulai")

    def test_invalid_penyelia_email_format(self):
        """Form tidak valid jika email penyelia tidak sesuai format."""
        form_data = {
            "role": "Intern",
            "total_jam_kerja": 300,
            "tanggal_mulai": "2024-06-01",
            "tanggal_selesai": "2024-09-01",
            "penyelia_nama": "Bad Email",
            "penyelia_perusahaan": "Invalid Corp",
            "penyelia_email": "invalid-email",  # format tidak valid
        }
        form = InputDetilKPForm(data=form_data, instance=self.pendaftaran_kp)
        self.assertFalse(form.is_valid())
        self.assertIn("penyelia_email", form.errors)

    def test_no_pending_registration_redirects(self):
        """User tanpa pendaftaran KP status 'Menunggu Detil' akan diarahkan."""
        self.client.login(username="testuser1", password="password")
        
        self.pendaftaran_kp.status_pendaftaran = "Terdaftar"
        self.pendaftaran_kp.save()

        response = self.client.get(reverse("input_detil:input_detil_kp_form"))
        self.assertRedirects(response, reverse("input_detil:no_pending_registration"))

    def test_form_save_with_commit_false(self):
        """Form.save(commit=False) tidak langsung menyimpan ke DB."""
        form_data = {
            "role": "Intern",
            "total_jam_kerja": 300,
            "tanggal_mulai": "2024-06-01",
            "tanggal_selesai": "2024-09-01",
            "penyelia_nama": "Commit Test",
            "penyelia_perusahaan": "Company",
            "penyelia_email": "commit@example.com",
        }
        form = InputDetilKPForm(data=form_data, instance=self.pendaftaran_kp)
        self.assertTrue(form.is_valid())

        updated_pendaftaran = form.save(commit=False)
        self.assertEqual(updated_pendaftaran.penyelia.nama, "Commit Test")

        # DB belum diperbarui
        self.pendaftaran_kp.refresh_from_db()
        self.assertNotEqual(self.pendaftaran_kp.penyelia.nama, "Commit Test")

    def test_input_detil_success_page_renders(self):
        """Test bahwa halaman input_detil_success dapat diakses dan menampilkan informasi yang benar."""
        self.client.login(username="testuser1", password="password")

        response = self.client.get(reverse("input_detil:input_detil_success", args=[self.pendaftaran_kp.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "success_page.html")
        self.assertContains(response, "Berhasil")  # Bisa disesuaikan tergantung isi template-mu
        self.assertContains(response, self.pendaftaran_kp.id)

