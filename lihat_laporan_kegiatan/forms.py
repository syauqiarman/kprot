# from django import forms
# from input_detil.models import LaporanKP, LaporanMBKM

# class PersetujuanLaporanForm(forms.ModelForm):
#     class Meta:
#         model = LaporanKP  # Default ke KP, nanti ditentukan di views
#         fields = ['disetujui_penyelia', 'feedback_penolakan_penyelia']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['feedback_penolakan_penyelia'].required = False

#     def clean(self):
#         cleaned_data = super().clean()
#         disetujui_penyelia = cleaned_data.get('disetujui_penyelia')
#         feedback = cleaned_data.get('feedback_penolakan_penyelia')
        
#         if disetujui_penyelia is False and not feedback:
#             self.add_error('feedback_penolakan_penyelia', 'Feedback wajib diberikan jika menolak.')

#         return cleaned_data