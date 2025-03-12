from datetime import datetime
from django.shortcuts import get_object_or_404
from database.models import PendaftaranKP, Mahasiswa
import json

# history_data = json.loads(registration.history) if registration.history else []
# history_data.append(datetime.now().isoformat())
# registration.history = json.dumps(history_data)

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
            status_pendaftaran="Menunggu Detil"
        )
    
    @staticmethod
    def update_registration_status(registration):
        """
        Perbarui status pendaftaran KP berdasarkan kelengkapan data:
        - Jika semua field penting terisi → status menjadi "Terdaftar"
        - Jika masih ada yang kosong → tetap "Menunggu Detil"
        """
        required_fields = [
            registration.role,
            registration.total_jam_kerja,
            registration.penyelia and registration.penyelia.nama,
            registration.penyelia and registration.penyelia.perusahaan,
            registration.penyelia and registration.penyelia.email,
        ]

        if all(required_fields):
            registration.status_pendaftaran = "Terdaftar"
        else:
            registration.status_pendaftaran = "Menunggu Detil"
        
        # registration.history.append(datetime.now().isoformat())  # Tambahkan timestamp
        # history_data = json.loads(registration.history) if registration.history else []
        # history_data.append(datetime.now().isoformat())
        # registration.history = json.dumps(history_data)
        registration.save()
        return registration
    
    @staticmethod
    def check_has_pending_registration(user):
        """Memeriksa apakah user memiliki pendaftaran yang masih 'Menunggu Detil'."""
        try:
            mahasiswa = Mahasiswa.objects.get(user=user)
            PendaftaranKP.objects.get(
                mahasiswa=mahasiswa,
                status_pendaftaran="Menunggu Detil"
            )
            return True
        except (Mahasiswa.DoesNotExist, PendaftaranKP.DoesNotExist):
            return False
