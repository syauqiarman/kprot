from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from input_detil.models import Mahasiswa, Semester, PendaftaranKP, Penyelia

class Command(BaseCommand):
    help = 'Deletes dummy data created for development purposes.'

    def handle(self, *args, **kwargs):
        # Delete the dummy user
        User.objects.filter(username='devuser').delete()

        # Delete the dummy Mahasiswa
        Mahasiswa.objects.filter(npm='123456789').delete()

        # Delete the dummy Semester
        Semester.objects.filter(nama='Semester Gasal 2024/2025').delete()

        # Delete the dummy PendaftaranKP
        PendaftaranKP.objects.filter(status_pendaftaran='Menunggu Detil').delete()

        PendaftaranKP.objects.filter(status_pendaftaran='Terdaftar').delete()

        # Delete the dummy Mahasiswa
        Penyelia.objects.filter(nama='titik').delete()

        self.stdout.write(self.style.SUCCESS('Dummy data deleted successfully!'))