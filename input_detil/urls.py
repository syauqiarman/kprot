from django.urls import path
from input_detil.views import input_detil_kp_form, no_pending_registration, input_detil_success, simpan_detil_kp

app_name = 'input_detil'

urlpatterns = [
    path('input-detil-kp-form/', input_detil_kp_form, name='input_detil_kp_form'),
    path('simpan/kp/<int:pendaftaran_id>', simpan_detil_kp, name='simpan_detil_kp'),
    path('no-pending/', no_pending_registration, name='no_pending_registration'),
    path("input-detil-kp-form/success/<int:pendaftaran_id>/", input_detil_success, name="input_detil_success"),
]