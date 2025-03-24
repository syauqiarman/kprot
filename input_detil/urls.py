from django.urls import path
from input_detil.views import input_detil_mbkm, no_pending_registration, input_detil_kp_form, input_detil_success, input_detil_mbkm_success

app_name = 'input_detil_program'

urlpatterns = [
    path('input-detil-kp-form/', input_detil_kp_form, name='input_detil_kp_form'),
    path('input-detil-mbkm/', input_detil_mbkm, name='input_detil_mbkm'),
    path('no-pending/', no_pending_registration, name='no_pending_registration'),
    path("input-detil-kp-form/success/<int:pendaftaran_id>/", input_detil_success, name="input_detil_success"),
    path('input-detil-mbkm/success/<int:pendaftaran_id>/', input_detil_mbkm_success, name='input_detil_mbkm_success'),
]
