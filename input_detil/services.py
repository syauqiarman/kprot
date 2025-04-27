from datetime import datetime
from django.shortcuts import get_object_or_404
from .models import PendaftaranKP, Mahasiswa, Penyelia, User
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string

class PendaftaranKPService:
    """
    Service class untuk menangani logika bisnis PendaftaranKP.
    """

    @staticmethod
    def get_pending_registration(user):
        """Mengambil pendaftaran KP yang masih 'Menunggu Detil' untuk user."""
        mahasiswa = get_object_or_404(Mahasiswa, user=user)
        return get_object_or_404(
            PendaftaranKP, 
            mahasiswa=mahasiswa,
            status_pendaftaran="Menunggu Detil",
            semester__aktif=True
        )
    
    @staticmethod
    def check_has_pending_registration(pendaftaran):
        """Memeriksa apakah user memiliki pendaftaran yang masih 'Menunggu Detil'."""
        if pendaftaran.semester.aktif == True and pendaftaran.status_pendaftaran == 'Menunggu Detil':
            return True
        else:
            return False

def pendaftaran_akun_penyelia(nama, perusahaan, email):
    existing_penyelia = Penyelia.objects.filter(email=email).first()
    existing_user = User.objects.filter(email=email).first()

    if existing_penyelia and existing_user:
        # Update data penyelia
        existing_penyelia.nama = nama
        existing_penyelia.perusahaan = perusahaan
        existing_penyelia.save()

        existing_user.nama = nama
        return existing_penyelia

    else:
        username = email.split('@')[0]
        user = User.objects.create(
            email=email,
            username=username,
        )
        temporary_password = get_random_string(length=10)
        user.set_password(temporary_password)
        user.save()

        penyelia = Penyelia.objects.create(
            user=user,
            nama=nama,
            perusahaan=perusahaan,
            email=email
        )

        print("tes masuk")
        send_mail(
            subject='Aktivasi Akun Penyelia siKP',
            message=(
                f"Yang kami hormati, Bapak/Ibu {nama},\n\n"
                f"Akun Anda sebagai penyelia telah berhasil didaftarkan.\n"
                f"Silakan login dengan kredensial berikut:\n\n"
                f"Username: {username}\n"
                f"Password sementara: {temporary_password}\n\n"
                f"Harap segera login dan ganti password Anda.\n\n"
                f"Terima kasih."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        print("tes keluar")

        return penyelia

