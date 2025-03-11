from django.test import RequestFactory, TestCase
from django.contrib.auth.models import User
from .views import daftar_kp
from .models import Mahasiswa, Semester
from .forms import PendaftaranKPForm

class PendaftaranKPFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.mahasiswa = Mahasiswa.objects.create(
            user=self.user, 
            nama="Budi", 
            email="test@example.com", 
            npm="123456789"
        )
        self.semester = Semester.objects.create(
            nama="Gasal 24/25", 
            gasal_genap="Gasal", 
            tahun=2024, 
            aktif=True
        )

        self.valid_data = {
            'semester': self.semester.id,
            'jumlah_semester': 6,
            'sks_lulus': 100,
            'pernyataan_komitmen': True,
        }

    # Test case positif
    def test_form_fields_disabled(self):
        form = PendaftaranKPForm(user=self.user)
        self.assertTrue(form.fields['nama'].disabled)
        self.assertTrue(form.fields['npm'].disabled)
        self.assertTrue(form.fields['email'].disabled)

    def test_valid_jumlah_semester(self):
        form = PendaftaranKPForm(data=self.valid_data, user=self.user)
        self.assertTrue(form.is_valid())

    def test_valid_max_jumlah_semester(self):
        valid_data = self.valid_data.copy()
        valid_data['jumlah_semester'] = 12
        form = PendaftaranKPForm(data=valid_data, user=self.user)
        self.assertTrue(form.is_valid())
    
    def test_valid_min_sks_lulus(self):
        valid_data = self.valid_data.copy()
        valid_data['sks_lulus'] = 100
        form = PendaftaranKPForm(data=valid_data, user=self.user)
        self.assertTrue(form.is_valid())
    
    def test_valid_high_sks_lulus(self):
        valid_data = self.valid_data.copy()
        valid_data['sks_lulus'] = 144
        form = PendaftaranKPForm(data=valid_data, user=self.user)
        self.assertTrue(form.is_valid())
    
    def test_valid_mid_sks_lulus(self):
        valid_data = self.valid_data.copy()
        valid_data['sks_lulus'] = 120
        form = PendaftaranKPForm(data=valid_data, user=self.user)
        self.assertTrue(form.is_valid())
    
    # Test case negatif
    def test_invalid_jumlah_semester(self):
        invalid_data = self.valid_data.copy()
        invalid_data['jumlah_semester'] = 4
        form = PendaftaranKPForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('jumlah_semester', form.errors)
        self.assertEqual(
            form.errors['__all__'][0],
            "Jumlah semester untuk mendaftar KP harus antara 6 hingga 12."
        )
    
    def test_invalid_sks_lulus(self):
        invalid_data = self.valid_data.copy()
        invalid_data['sks_lulus'] = 99
        form = PendaftaranKPForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertEqual(
            form.errors['__all__'][0],
            "Jumlah SKS lulus untuk mendaftar KP harus antara 100 hingga 144."
        )
    
    def test_missing_required_fields(self):
        required_fields = ['jumlah_semester', 'sks_lulus', 'pernyataan_komitmen']
        for field in required_fields:
            invalid_data = self.valid_data.copy()
            del invalid_data[field]
            form = PendaftaranKPForm(data=invalid_data, user=self.user)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)
    
    def test_unchecked_pernyataan_komitmen(self):
        invalid_data = self.valid_data.copy()
        invalid_data['pernyataan_komitmen'] = False
        form = PendaftaranKPForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('pernyataan_komitmen', form.errors)
    
    def test_invalid_high_jumlah_semester(self):
        invalid_data = self.valid_data.copy()
        invalid_data['jumlah_semester'] = 13
        form = PendaftaranKPForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
    
    def test_invalid_low_sks_lulus(self):
        invalid_data = self.valid_data.copy()
        invalid_data['sks_lulus'] = 50
        form = PendaftaranKPForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
    
    def test_invalid_extreme_high_sks_lulus(self):
        invalid_data = self.valid_data.copy()
        invalid_data['sks_lulus'] = 300
        form = PendaftaranKPForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())


###Views tests###

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import PendaftaranKP, Mahasiswa, Semester

class PendaftaranKPViewTests(TestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
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

        self.valid_data = {
            'semester': self.semester.id,
            'jumlah_semester': 6,
            'sks_lulus': 120,
            'pernyataan_komitmen': True,
        }

    def test_daftar_kp(self):
        request = self.factory.post(reverse('PendaftaranMahasiswa:pendaftaran_kp'), data=self.valid_data)
        request.user = self.user
        response = daftar_kp(request)
        self.assertEqual(response.status_code, 302) 
        self.assertEqual(PendaftaranKP.objects.count(), 1)

    def test_daftar_kp_invalid_form_semester(self):
        invalid_data = self.valid_data.copy()
        invalid_data['jumlah_semester'] = 4 
        request = self.factory.post(reverse('PendaftaranMahasiswa:pendaftaran_kp'), data=invalid_data)
        request.user = self.user
        response = daftar_kp(request)
        self.assertEqual(response.status_code, 200)  
        self.assertContains(response, "Jumlah semester untuk mendaftar KP harus antara 6 hingga 12.")

    def test_daftar_kp_invalid_form_sks(self):
        invalid_data = self.valid_data.copy()
        invalid_data['sks_lulus'] = 0 
        request = self.factory.post(reverse('PendaftaranMahasiswa:pendaftaran_kp'), data=invalid_data)
        request.user = self.user
        response = daftar_kp(request)
        self.assertEqual(response.status_code, 200)  
        self.assertContains(response, "Jumlah SKS lulus untuk mendaftar KP harus antara 100 hingga 144.")


    def test_daftar_kp_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse('PendaftaranMahasiswa:pendaftaran_kp'))
        self.assertEqual(response.status_code, 302)  

    def test_kp_berhasil_page(self):
        pendaftaran = PendaftaranKP.objects.create(
            mahasiswa=self.mahasiswa,
            semester=self.semester,
            jumlah_semester=6,
            sks_lulus=100,
            pernyataan_komitmen=True,
            status_pendaftaran="Menunggu Detil",
            history=[]
        )
        response = self.client.get(reverse('PendaftaranMahasiswa:kp_berhasil', args=[pendaftaran.id]))
        self.assertEqual(response.status_code, 302)

