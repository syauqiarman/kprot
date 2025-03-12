from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from input_detil.models import Mahasiswa, Semester, PendaftaranKP, PembimbingAkademik

class Command(BaseCommand):
    help = 'Creates dummy data for development purposes.'

    def handle(self, *args, **kwargs):
        # Create a dummy user
        user, created = User.objects.get_or_create(
            username='devuser',
            defaults={'email': 'devuser@example.com', 'password': 'password123'}
        )

        user2, created = User.objects.get_or_create(
            username='padevuser',
            defaults={'email': 'sutopo@example.com', 'password': 'password123'}
        )

        # Create a dummy Pembimbing Akademik
        pa, created = PembimbingAkademik.objects.get_or_create(
            user=user2,
            defaults={'nama': 'Dr. Sutopo', 'email': 'sutopo@example.com'}
            )

        # Create a dummy Mahasiswa
        mahasiswa, created = Mahasiswa.objects.get_or_create(
            user=user,
            defaults={
                'nama': 'John Doe',
                'npm': '123456789',
                'email': 'johndoe@example.com',  # Add the required email field
                'pa': pa
            }
        )

        # Create a dummy Semester
        semester, created = Semester.objects.get_or_create(
            defaults={'nama': 'Semester Gasal 2024/2025',
                      'tahun': 2025,
                      'gasal_genap': 'Gasal',
                      'aktif': True}
        )

        # Create a dummy PendaftaranKP with status "Menunggu Detil"
        pendaftaran_kp, created = PendaftaranKP.objects.get_or_create(
            mahasiswa=mahasiswa,
            semester=semester,
            defaults={'jumlah_semester': 7, 'sks_lulus': 120, 'pernyataan_komitmen': True, 'status_pendaftaran': 'Menunggu Detil'}
        )

        if created:
            self.stdout.write(self.style.SUCCESS('Dummy data created successfully!'))
        else:
            self.stdout.write(self.style.WARNING('Dummy data already exists.'))