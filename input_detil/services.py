from datetime import datetime
from django.shortcuts import get_object_or_404
from .models import PendaftaranKP, Mahasiswa

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

