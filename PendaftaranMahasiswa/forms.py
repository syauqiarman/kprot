from django import forms
from .models import PendaftaranKP

class PendaftaranKPForm(forms.ModelForm):
    class Meta:
        model = PendaftaranKP
        fields = [
            'mahasiswa', 'semester', 'jumlah_semester', 'sks_diambil', 'sks_lulus',
            'penyelia', 'role', 'total_jam_kerja', 'tanggal_mulai', 'tanggal_selesai',
            'pernyataan_komitmen', 'status_pendaftaran'
        ]
    
    def clean(self):
        cleaned_data = super().clean()
        sks_lulus = cleaned_data.get('sks_lulus')
        semester = cleaned_data.get('jumlah_semester')
        
        if sks_lulus is not None and sks_lulus < 100:
            raise forms.ValidationError("Anda tidak memenuhi syarat karena SKS Lulus kurang dari 100.")
        
        if semester is not None and semester < 6:
            raise forms.ValidationError("Anda tidak memenuhi syarat karena Semester kurang dari 6.")
        
        pernyataan_komitmen = cleaned_data.get('pernyataan_komitmen')
        if not pernyataan_komitmen:
            raise forms.ValidationError("Anda harus menyetujui pernyataan komitmen.")
        
        return cleaned_data
