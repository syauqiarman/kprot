from django.contrib.auth.models import Group
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from datetime import date
from django.contrib.auth.models import User
from .models import *
from testapp.filters import MahasiswaFilter

class BaseMahasiswaViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

        # Users
        self.user_20 = User.objects.create_user(username='mahasiswa20', password='password')
        self.user_21 = User.objects.create_user(username='mahasiswa21', password='password')
        self.user_22 = User.objects.create_user(username='mahasiswa22', password='password')
        self.user_penyelia = User.objects.create_user(username='penyelia', password='password')
        self.user_pa = User.objects.create_user(username="pa_user", password="password")
        self.user_dosen = User.objects.create_user(username="dosen_user", password="password")
        self.user_manajemen = User.objects.create_user(username="manajemen_user", password="password")

        # Roles
        self.pa = PembimbingAkademik.objects.create(user=self.user_pa, nama="PA", email="pa@example.com")
        self.dosen = Dosen.objects.create(user=self.user_dosen, nama="Dosen", email="dosen@example.com")
        self.manajemen = Manajemen.objects.create(user=self.user_manajemen, nama="manajemen", email="manajemen@example.com")
        self.penyelia = Penyelia.objects.create(user=self.user_penyelia, nama="Siti", perusahaan="TechCorp", email="siti@corp.com")

        # Semesters
        self.semester_2025 = Semester.objects.create(nama="Gasal 2025", gasal_genap="Gasal", tahun=2025, aktif=False)
        self.semester_2026 = Semester.objects.create(nama="Genap 2026", gasal_genap="Genap", tahun=2026, aktif=False)
        self.semester_2027 = Semester.objects.create(nama="Gasal 2027", gasal_genap="Gasal", tahun=2027, aktif=True)

        # Mahasiswa
        self.mahasiswa_20 = Mahasiswa.objects.create(user=self.user_20, nama="Andi", npm="200123456", email="andi@example.com", pa=self.pa)
        self.mahasiswa_21 = Mahasiswa.objects.create(user=self.user_21, nama="Budi", npm="210123456", email="budi@example.com", pa=self.pa)
        self.mahasiswa_22 = Mahasiswa.objects.create(user=self.user_22, nama="Caca", npm="220123456", email="caca@example.com", pa=self.pa)
        
        self.queryset = Mahasiswa.objects.all()

        # Program MBKM
        self.program_mbkm = ProgramMBKM.objects.create(nama="Magang Mandiri", minimum_sks=10, maksimum_sks=20)

        # Pendaftaran
        self.pendaftaran_kp1 = PendaftaranKP.objects.create(
            mahasiswa=self.mahasiswa_20, semester=self.semester_2026, jumlah_semester=7,
            sks_lulus=120, penyelia=self.penyelia, role="Software Engineer", total_jam_kerja=300,
            tanggal_mulai=date(2025, 10, 2), tanggal_selesai=date(2026, 4, 29), pernyataan_komitmen=True
        )
        self.pendaftaran_kp2 = PendaftaranKP.objects.create(
            mahasiswa=self.mahasiswa_21, semester=self.semester_2027, jumlah_semester=7,
            sks_lulus=120, penyelia=self.penyelia, role="Software Engineer", total_jam_kerja=300,
            tanggal_mulai=date(2027, 4, 2), tanggal_selesai=date(2027, 10, 30), pernyataan_komitmen=True
        )
        self.pendaftaran_mbkm1 = PendaftaranMBKM.objects.create(
            mahasiswa=self.mahasiswa_22, semester=self.semester_2027, jumlah_semester=7, sks_diambil=12,
            rencana_lulus_semester_ini=False, program_mbkm=self.program_mbkm, penyelia=self.penyelia,
            role="Software Engineer", estimasi_sks_konversi=10, tanggal_mulai=date(2027, 7, 2),
            tanggal_selesai=date(2028, 1, 30), pernyataan_komitmen=True
        )

        # Create a dummy request for filter testing
        self.dummy_request = self.factory.get('/')
        self.dummy_request.resolver_match = type('obj', (object,), {
            'kwargs': {'semester_id': self.semester_2027.id}
        })


# Tests untuk list_semester
class ListSemesterViewTests(BaseMahasiswaViewTest):
    def test_list_semester_access_positive(self):
        for user in [self.user_dosen, self.user_pa, self.user_manajemen]:
            self.client.login(username=user.username, password="password")
            response = self.client.get(reverse('testapp:list_semester'))
            self.assertEqual(response.status_code, 200)
            self.client.logout()

    def test_list_semester_access_negative(self):
        for user in [self.user_20, self.user_21, self.user_22, self.user_penyelia]:
            self.client.login(username=user.username, password="password")
            response = self.client.get(reverse('testapp:list_semester'))
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith('/login/'))
            self.client.logout()

# Tests untuk list_mahasiswa
class testappViewTests(BaseMahasiswaViewTest):
    def test_list_mahasiswa_access_positive(self):
        for user in [self.user_dosen, self.user_pa, self.user_manajemen]:
            self.client.login(username=user.username, password="password")
            response = self.client.get(reverse('testapp:list_mahasiswa', args=[self.semester_2027.id]))
            self.assertEqual(response.status_code, 200)
            self.client.logout()

    def test_list_mahasiswa_access_negative(self):
        for user in [self.user_20, self.user_21, self.user_22, self.user_penyelia]:
            self.client.login(username=user.username, password="password")
            response = self.client.get(reverse('testapp:list_mahasiswa', args=[self.semester_2027.id]))
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith('/login/'))
            self.client.logout()

    def test_list_mahasiswa_post_method_not_allowed(self):
        self.client.login(username=self.user_dosen.username, password="password")
        response = self.client.post(reverse('testapp:list_mahasiswa', args=[self.semester_2027.id]))
        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, {"error": "Method not allowed"})
        self.client.logout()

    def test_list_mahasiswa_use_active_semester(self):
        self.client.login(username=self.user_pa.username, password="password")
        response = self.client.get(reverse('testapp:list_mahasiswa_no_id'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Caca")
        self.client.logout()

    def test_list_mahasiswa_no_active_semester_returns_404(self):
        Semester.objects.update(aktif=False)
        self.client.login(username=self.user_pa.username, password="password")
        response = self.client.get(reverse('testapp:list_mahasiswa_no_id'))
        self.assertEqual(response.status_code, 404)
        self.client.logout()

    def test_pa_only_sees_own_students(self):
        self.client.login(username=self.user_pa.username, password="password")
        response = self.client.get(reverse('testapp:list_mahasiswa', args=[self.semester_2027.id]))
        self.assertContains(response, "Caca")
        self.client.logout()

    def test_pa_sees_own_and_program_students_only(self):
        user_other = User.objects.create_user(username='mahasiswaX', password='password')
        Mahasiswa.objects.create(user=user_other, nama="Xavier", npm="230123456", email="x@example.com", pa=None)

        self.client.login(username=self.user_pa.username, password="password")
        response = self.client.get(reverse('testapp:list_mahasiswa', args=[self.semester_2027.id]))
        self.assertContains(response, "Caca")
        self.assertNotContains(response, "Xavier")
        self.client.logout()
    
    def test_pa_double_role(self):
        # Menambahkan user_pa sebagai Dosen juga
        Dosen.objects.create(user=self.user_pa, nama="PA sebagai Dosen", email="dualpa@example.com")

        # Login dengan user yang merupakan PA dan juga Dosen
        self.client.login(username=self.user_pa.username, password="password")
        response = self.client.get(reverse('testapp:list_mahasiswa', args=[self.semester_2027.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Caca")  # Mahasiswa yang dibimbing oleh PA
        self.assertContains(response, "Budi")  # Mahasiswa terdaftar di semester
        self.client.logout()

    def test_pa_also_as_manajemen_gets_combined_filtering(self):
        self.user_pa.groups.add(Group.objects.get_or_create(name="manajemen")[0])
        Manajemen.objects.create(user=self.user_pa, nama="PA-manajemen", email="dual@example.com")

        self.client.login(username=self.user_pa.username, password="password")
        response = self.client.get(reverse('testapp:list_mahasiswa', args=[self.semester_2027.id]))
        
        self.assertContains(response, "Caca") 
        self.assertContains(response, "Budi") 
        self.client.logout()

# Tests untuk filtering mahasiswa
class MahasiswaFilterTests(BaseMahasiswaViewTest):
    def test_filter_by_program_kp(self):
        filter_instance = MahasiswaFilter(request=self.dummy_request)
        result = filter_instance.filter_by_program(self.queryset, "program", "KP")
        self.assertEqual(result.count(), 1)
        self.assertIn(self.mahasiswa_21, result)

    def test_filter_by_program_mbkm(self):
        filter_instance = MahasiswaFilter(request=self.dummy_request)
        result = filter_instance.filter_by_program(self.queryset, "program", "MBKM")
        self.assertEqual(result.count(), 1)
        self.assertIn(self.mahasiswa_22, result)

    def test_filter_by_program_all(self):
        filter_instance = MahasiswaFilter(request=self.dummy_request)
        result = filter_instance.filter_by_program(self.queryset, "program", "")
        self.assertEqual(result.count(), 3)

    def test_filter_by_program_no_matches(self):
        PendaftaranKP.objects.all().delete()
        PendaftaranMBKM.objects.all().delete()
        filter_instance = MahasiswaFilter(request=self.dummy_request)
        result_kp = filter_instance.filter_by_program(self.queryset, "program", "KP")
        result_mbkm = filter_instance.filter_by_program(self.queryset, "program", "MBKM")
        self.assertEqual(result_kp.count(), 0)
        self.assertEqual(result_mbkm.count(), 0)

    def test_filter_by_program_invalid_value(self):
        filter_instance = MahasiswaFilter(request=self.dummy_request)
        result = filter_instance.filter_by_program(self.queryset, "program", "INVALID")
        self.assertEqual(result.count(), 3)

    def test_filter_by_status_kp_match(self):
        self.pendaftaran_kp1.status_pendaftaran = "Menunggu Detil"
        self.pendaftaran_kp1.save()
        filter_instance = MahasiswaFilter(request=self.dummy_request)
        result = filter_instance.filter_by_status(self.queryset, "status", "Menunggu Detil")
        self.assertIn(self.mahasiswa_21, result)

    def test_filter_by_status_mbkm_match(self):
        self.pendaftaran_mbkm1.status_pendaftaran = "Menunggu Verifikasi Dosen"
        self.pendaftaran_mbkm1.save()
        filter_instance = MahasiswaFilter(request=self.dummy_request)
        result = filter_instance.filter_by_status(self.queryset, "status", "Menunggu Verifikasi Dosen")
        self.assertIn(self.mahasiswa_22, result)

    def test_filter_by_status_no_match(self):
        self.pendaftaran_kp1.status_pendaftaran = "Menunggu Detil"
        self.pendaftaran_kp2.status_pendaftaran = "Menunggu Detil"
        self.pendaftaran_mbkm1.status_pendaftaran = "Menunggu Persetujuan PA"
        self.pendaftaran_kp1.save()
        self.pendaftaran_kp2.save()
        self.pendaftaran_mbkm1.save()
        filter_instance = MahasiswaFilter(request=self.dummy_request)
        result = filter_instance.filter_by_status(self.queryset, "status", "Terdaftar")
        self.assertEqual(result.count(), 0)

    # Tests untuk semester handling di filter_by_program
    def test_filter_by_program_with_active_semester_positive(self):
        # Test positif: Semester aktif tersedia
        request_without_semester = self.factory.get('/')
        request_without_semester.resolver_match = type('obj', (object,), {'kwargs': {}})
        
        filter_instance = MahasiswaFilter(request=request_without_semester)
        result = filter_instance.filter_by_program(self.queryset, "program", "KP")
        
        # Harus bisa menemukan mahasiswa dengan pendaftaran KP di semester aktif
        self.assertIn(self.mahasiswa_21, result)
        
    def test_filter_by_program_no_active_semester_negative(self):
        # Test negatif: Tidak ada semester aktif
        Semester.objects.update(aktif=False)
        
        request_without_semester = self.factory.get('/')
        request_without_semester.resolver_match = type('obj', (object,), {'kwargs': {}})
        
        filter_instance = MahasiswaFilter(request=request_without_semester)
        result = filter_instance.filter_by_program(self.queryset, "program", "KP")
        
        # Harus mengembalikan queryset asli tanpa filtering
        self.assertEqual(result.count(), 3)
        
    def test_filter_by_program_invalid_semester_id_corner(self):
        # Corner case: semester_id valid tapi semester tidak ditemukan
        request_with_invalid_semester = self.factory.get('/')
        request_with_invalid_semester.resolver_match = type('obj', (object,), {'kwargs': {'semester_id': 9999}})
        
        filter_instance = MahasiswaFilter(request=request_with_invalid_semester)
        result = filter_instance.filter_by_program(self.queryset, "program", "KP")
        
        # Harus mengembalikan queryset asli tanpa filtering
        self.assertEqual(result.count(), 3)
        
    # Tests untuk semester handling di filter_by_status
    def test_filter_by_status_with_active_semester_positive(self):
        # Test positif: Semester aktif tersedia
        self.pendaftaran_kp2.status_pendaftaran = "Terdaftar"
        self.pendaftaran_kp2.save()
        
        request_without_semester = self.factory.get('/')
        request_without_semester.resolver_match = type('obj', (object,), {'kwargs': {}})
        
        filter_instance = MahasiswaFilter(request=request_without_semester)
        result = filter_instance.filter_by_status(self.queryset, "status", "Terdaftar")
        
        # Harus bisa menemukan mahasiswa dengan status di semester aktif
        self.assertIn(self.mahasiswa_21, result)
        
    def test_filter_by_status_no_active_semester_negative(self):
        # Test negatif: Tidak ada semester aktif
        Semester.objects.update(aktif=False)
        
        request_without_semester = self.factory.get('/')
        request_without_semester.resolver_match = type('obj', (object,), {'kwargs': {}})
        
        filter_instance = MahasiswaFilter(request=request_without_semester)
        result = filter_instance.filter_by_status(self.queryset, "status", "Terdaftar")
        
        # Harus mengembalikan queryset asli tanpa filtering
        self.assertEqual(result.count(), 3)
        
    def test_filter_by_status_invalid_semester_id_corner(self):
        # Corner case: semester_id valid tapi semester tidak ditemukan
        request_with_invalid_semester = self.factory.get('/')
        request_with_invalid_semester.resolver_match = type('obj', (object,), {'kwargs': {'semester_id': 9999}})
        
        filter_instance = MahasiswaFilter(request=request_with_invalid_semester)
        result = filter_instance.filter_by_status(self.queryset, "status", "Terdaftar")
        
        # Harus mengembalikan queryset asli tanpa filtering
        self.assertEqual(result.count(), 3)

