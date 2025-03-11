from django.urls import path
from input_detil.views import InputDetilKPView, input_detil_kp_form, no_pending_registration, input_detil_success

app_name = 'input_detil'

urlpatterns = [
    # Class-based view option
    path('input-detil-kp/', InputDetilKPView.as_view(), name='input_detil_kp'),
    # Function-based view option
    path('input-detil-kp-form/', input_detil_kp_form, name='show_input_detil_kp_form'),
    path('no-pending/', no_pending_registration, name='no_pending_registration'),
    path("input-detil-kp-form/success/<int:pendaftaran_id>/", input_detil_success, name="input_detil_success"),
]