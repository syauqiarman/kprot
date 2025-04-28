from django.test import TestCase
import unittest, requests, pytest, jwt, requests
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime, timedelta,timezone
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.utils import timezone
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from sso_ui.ticket import validate_ticket, ValidateTicketError
from sso_ui.orgs import get_organizations, get_organization
from sso_ui.utils import create_token, decode_token, validate_ticket
from sso_ui.config import SSOJWTConfig

class UtilsTest(unittest.TestCase):
    def setUp(self):
        self.config = SSOJWTConfig()
        self.user_data = {
            "username": "testuser",
            "nama": "Test User",
            "npm": "12345678",
            "organization": {
                "faculty": "Ilmu Komputer",
                "shortFaculty": "Fasilkom",
                "major": "Ilmu Komputer",
                "program": "S1 Reguler"
            }
        }

    def test_create_token(self):
        token = create_token(self.user_data, "access")
        decoded = jwt.decode(token, self.config.access_token_secret_key, algorithms=["HS256"])
        self.assertEqual(decoded["username"], "testuser")
        self.assertEqual(decoded["nama"], "Test User")
        self.assertEqual(decoded["npm"], "12345678")
        self.assertIn("exp", decoded)

    def test_decode_valid_token(self):
        token = create_token(self.user_data, "access")
        decoded = decode_token(token, "access")
        self.assertEqual(decoded["username"], "testuser")

    def test_decode_expired_token(self):
        expired_token = jwt.encode(
            {
                "iat": datetime.now(timezone.utc),
                "exp": datetime.now(timezone.utc) - timedelta(seconds=1), 
                "username": "testuser"
            },
            self.config.access_token_secret_key,
            algorithm="HS256"
        )
        self.assertIsNone(decode_token(expired_token, "access"))

    def test_decode_invalid_token(self):
        self.assertIsNone(decode_token("invalid.token.here", "access"))

    @patch("sso_ui.utils.requests.get")
    def test_validate_ticket_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">
            <cas:authenticationSuccess>
                <cas:user>testuser</cas:user>
                <cas:attributes>
                    <cas:nama>Test User</cas:nama>
                    <cas:npm>12345678</cas:npm>
                </cas:attributes>
            </cas:authenticationSuccess>
        </cas:serviceResponse>"""
        mock_get.return_value = mock_response

        result = validate_ticket("valid_ticket")
        self.assertEqual(result["username"], "testuser")
        self.assertEqual(result["nama"], "Test User")
        self.assertEqual(result["npm"], "12345678")

    @patch("sso_ui.utils.requests.get")
    def test_validate_ticket_invalid_ticket(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">
            <cas:authenticationFailure code="INVALID_TICKET">
                Ticket not recognized
            </cas:authenticationFailure>
        </cas:serviceResponse>"""
        mock_get.return_value = mock_response

        self.assertIsNone(validate_ticket("invalid_ticket"))

    @patch("sso_ui.utils.requests.get")
    def test_validate_ticket_request_error(self, mock_get):
        mock_get.side_effect = requests.RequestException("Request failed")
        self.assertIsNone(validate_ticket("request_error"))

    @patch("sso_ui.utils.requests.get")
    def test_validate_ticket_xml_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """<invalid>"""
        mock_get.return_value = mock_response

        self.assertIsNone(validate_ticket("invalid_xml"))
    
    @patch("sso_ui.utils.requests.get")
    def test_validate_ticket_missing_user(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">
            <cas:authenticationSuccess>
                <cas:attributes>
                    <cas:nama>Test User</cas:nama>
                    <cas:npm>12345678</cas:npm>
                </cas:attributes>
            </cas:authenticationSuccess>
        </cas:serviceResponse>"""
        
        mock_get.return_value = mock_response
        self.assertIsNone(validate_ticket("missing_user"))

    @patch("sso_ui.utils.requests.get")
    def test_validate_ticket_empty_user(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">
            <cas:authenticationSuccess>
                <cas:user></cas:user>
                <cas:attributes>
                    <cas:nama>Test User</cas:nama>
                    <cas:npm>12345678</cas:npm>
                </cas:attributes>
            </cas:authenticationSuccess>
        </cas:serviceResponse>"""
        
        mock_get.return_value = mock_response
        self.assertIsNone(validate_ticket("empty_user"))

    @patch("sso_ui.utils.requests.get")
    def test_validate_ticket_no_attributes(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Tidak ada <cas:attributes> di XML
        mock_response.text = """<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">
            <cas:authenticationSuccess>
                <cas:user>testuser</cas:user>
            </cas:authenticationSuccess>
        </cas:serviceResponse>"""
        mock_get.return_value = mock_response

        result = validate_ticket("ticket_no_attributes")
        self.assertIsNotNone(result)
        self.assertEqual(result["username"], "testuser")
        self.assertEqual(len(result), 1)

class TokenTest(unittest.TestCase):
    """Test suite untuk pengujian pembuatan dan decoding JWT dalam SSO authentication."""

    def setUp(self):
        """Menyiapkan konfigurasi test dan contoh respons autentikasi SSO."""
        self.config = SSOJWTConfig()
        self.sample_sso_response = {
            "authentication_success": {
                "user": "testuser",
                "attributes": {
                    "nama": "Test User",
                    "npm": "12345678",
                    "kd_org": "01.00.12.01",
                    "peran_user": "staff"
                }
            }
        }
        # Pastikan setiap pemanggilan _get_user_organization mengembalikan "Ilmu Komputer"
        patcher = patch("sso_ui.token.orgs.get_organization", return_value="Ilmu Komputer")
        self.mock_get_org = patcher.start()
        self.addCleanup(patcher.stop)

    ### ENCODE TOKEN ###
    
    def test_create_token_with_sso_role(self):
        """Memastikan bahwa peran dari SSO ditetapkan dengan benar dalam JWT."""
        roles_to_test = {"dosen": "dosen"}
        for sso_role, expected_role in roles_to_test.items():
            with self.subTest(sso_role=sso_role):
                self.sample_sso_response["authentication_success"]["attributes"]["peran_user"] = sso_role
                token = create_token(self.config, "access_token", self.sample_sso_response)
                decoded = self._decode_token("access_token", token)
                self.assertEqual(decoded["role"], expected_role)

    @pytest.mark.django_db
    @patch.object(get_user_model(), "objects")
    def test_create_token_with_database_role(self, mock_user_objects):
        """Memastikan bahwa jika user ada di database, peran dari database akan digunakan."""
        mock_user = MagicMock()
        mock_user.role = "pengawas"
        mock_user_objects.get.return_value = mock_user  
        # Set peran SSO tidak valid sehingga memicu pencarian dari database
        self.sample_sso_response["authentication_success"]["attributes"]["peran_user"] = "invalid_role"
        token = create_token(self.config, "access_token", self.sample_sso_response)
        decoded = self._decode_token("access_token", token)
        self.assertEqual(decoded["role"], "pengawas")

    @patch.object(get_user_model(), "objects")
    def test_create_token_for_nonexistent_user(self, mock_user_objects):
        """Memastikan bahwa jika user tidak ditemukan, peran default 'pengguna' digunakan."""
        mock_user_objects.get.side_effect = get_user_model().DoesNotExist
        self.sample_sso_response["authentication_success"]["attributes"]["peran_user"] = "invalid_role"
        token = create_token(self.config, "access_token", self.sample_sso_response)
        decoded = self._decode_token("access_token", token)
        self.assertEqual(decoded["role"], "pengguna")
    
    def test_create_token_with_missing_user_data(self):
        """Memastikan bahwa jika tidak ada data user, fungsi akan memunculkan Exception."""
        invalid_response = {"authentication_success": None}
        with self.assertRaises(Exception) as context:
            create_token(self.config, "access_token", invalid_response)
        self.assertEqual(str(context.exception), "Authentication failed: no user data")

    @pytest.mark.django_db
    @patch("sso_ui.token.RefreshToken")
    def test_create_refresh_token(self, mock_refresh):
        """Memastikan bahwa refresh token berhasil dibuat dan valid."""
        # Siapkan instance refresh token palsu dengan klaim organization yang valid
        fake_token = RefreshToken()
        fake_token["organization"] = "Ilmu Komputer"
        mock_refresh.return_value = fake_token
        token = create_token(self.config, "refresh_token", self.sample_sso_response)
        decoded = decode_token(self.config, "refresh_token", token)
        self.assertIsNotNone(decoded, "Refresh token gagal dibuat atau tidak valid")
        self.assertIn("username", decoded, "Refresh token tidak mengandung username")
        self.assertIn("role", decoded, "Refresh token tidak mengandung role")

    @pytest.mark.django_db
    def test_create_token_invalid_type(self):
        """Memastikan bahwa jika token_type tidak valid, akan memunculkan ValueError."""
        with self.assertRaises(ValueError) as context:
            create_token(self.config, "invalid_token_type", self.sample_sso_response)
        self.assertEqual(str(context.exception), "Invalid token type")

    ### DECODE TOKEN ###
    
    def test_decode_access_token(self):
        """Memastikan decoding access token berhasil."""
        token = self._generate_token("access_token", "pengguna")
        decoded = decode_token(self.config, "access_token", token)
        self.assertIsNotNone(decoded, "Access token failed to decode")
        self.assertEqual(decoded["username"], "testuser")

    def test_decode_refresh_token(self):
        """Memastikan decoding refresh token berhasil dan mengambil data yang benar."""
        token = self._generate_token("refresh_token", "pengguna")
        decoded = self._decode_token("refresh_token", token)
        self.assertIsNotNone(decoded, "Refresh token failed to decode")
        self.assertEqual(decoded["username"], "testuser")

    def test_decode_expired_token(self):
        """Memastikan bahwa token yang sudah kadaluarsa tidak dapat digunakan."""
        # Buat token expired dengan jeda yang cukup besar
        expired_token = self._generate_token("access_token", "pengguna", expired=True, offset=3600)
        decoded = self._decode_token("access_token", expired_token)
        self.assertIsNone(decoded, "Token yang expired masih dianggap valid!")

    def test_decode_invalid_token(self):
        """Memastikan bahwa token yang tidak valid dikembalikan sebagai None."""
        decoded = self._decode_token("access_token", "invalid.token.value")
        self.assertIsNone(decoded)

    def test_decode_token_with_invalid_role(self):
        """Memastikan bahwa token dengan peran tidak valid ditolak."""
        token = self._generate_token("access_token", "invalid_role")
        decoded = self._decode_token("access_token", token)
        self.assertIsNone(decoded)

    def test_decode_invalid_token_type(self):
        """Memastikan bahwa penggunaan tipe token yang tidak valid akan memunculkan ValueError."""
        with self.assertRaises(ValueError):
            decode_token(self.config, "invalid_token_type", "random.token.value")
    
    def test_generate_token_invalid_type(self):
        """Pastikan `_generate_token()` me-raise ValueError jika tipe token invalid."""
        with self.assertRaises(ValueError) as ctx:
            self._generate_token("invalid_type", "pengguna")
        self.assertEqual(str(ctx.exception), "Invalid token type")

    @patch('sso_ui.token.UntypedToken', side_effect=TokenError("Invalid token"))
    def test_decode_token_tokenerror(self, mock_untypedtoken):
        """Memastikan bahwa jika UntypedToken melempar TokenError, decode_token mengembalikan None."""
        decoded = decode_token(self.config, "access_token", "any.token.value")
        self.assertIsNone(decoded)

    @patch('sso_ui.token.UntypedToken')
    def test_decode_token_without_exp(self, mock_untypedtoken):
        """Memastikan bahwa jika token tidak memiliki field 'exp', decode_token mengembalikan claims dengan role yang valid."""
        # Buat dummy claims tanpa "exp", tetapi sertakan organization
        dummy_claims = {
            "username": "testuser",
            "role": "pengguna",
            "organization": "Ilmu Komputer"
        }
        dummy_token = "dummy.token.value"
        instance = MagicMock()
        instance.payload = dummy_claims
        mock_untypedtoken.return_value = instance
        decoded = decode_token(self.config, "access_token", dummy_token)
        self.assertEqual(decoded, dummy_claims)

    def test_decode_access_token_with_org_dict_valid(self):
        """Memastikan decoding access token dengan organization berupa dict valid."""
        token = AccessToken()
        token["username"] = "testuser"
        token["role"] = "pengguna"
        token["organization"] = {"faculty": "Ilmu Komputer"}
        token["exp"] = int(timezone.now().timestamp() + 600)
        token_str = str(token)
        decoded = decode_token(self.config, "access_token", token_str)
        # Pastikan token ter-decode dengan benar
        self.assertIsInstance(decoded, dict)
        self.assertEqual(decoded["username"], "testuser")

    def test_decode_access_token_with_org_dict_invalid(self):
        """
        Memastikan decoding access token dengan organization berupa dict
        tetapi faculty bukan 'Ilmu Komputer' => Response 401
        """
        token = AccessToken()
        token["username"] = "testuser"
        token["role"] = "pengguna"
        token["organization"] = {"faculty": "Not Ilmu Komputer"}
        token["exp"] = int(timezone.now().timestamp() + 600)
        token_str = str(token)
        decoded = decode_token(self.config, "access_token", token_str)
        self.assertIsInstance(decoded, Response)
        self.assertEqual(decoded.status_code, 401)

    def test_decode_access_token_with_no_org(self):
        """Memastikan jika organization None => langsung Response 401."""
        token = AccessToken()
        token["username"] = "testuser"
        token["role"] = "pengguna"
        # Tanpa 'organization'
        token["exp"] = int(timezone.now().timestamp() + 600)
        token_str = str(token)
        decoded = decode_token(self.config, "access_token", token_str)
        self.assertIsInstance(decoded, Response)
        self.assertEqual(decoded.status_code, 401)

    def test_decode_access_token_with_other_org(self):
        """Memastikan jika organization string bukan 'Ilmu Komputer' => langsung Response 401."""
        token = AccessToken()
        token["username"] = "testuser"
        token["role"] = "pengguna"
        token["organization"] = "Teknik"
        token["exp"] = int(timezone.now().timestamp() + 600)
        token_str = str(token)
        decoded = decode_token(self.config, "access_token", token_str)
        self.assertIsInstance(decoded, Response)
        self.assertEqual(decoded.status_code, 401)

    @patch('sso_ui.token.UntypedToken')
    def test_decode_token_expired_claim(self, mock_untypedtoken):
        """
        Menguji jika 'exp' pada claims sudah kedaluwarsa (exp_time < now).
        """
        expired_claims = {
            "exp": int(timezone.now().timestamp()) - 10,  # waktu di masa lalu
            "role": "pengguna",                          # role valid
            "organization": "Ilmu Komputer",             # organisasi valid
            "username": "testuser"
        }
        mock_instance = MagicMock()
        mock_instance.payload = expired_claims
        mock_untypedtoken.return_value = mock_instance

        result = decode_token(self.config, "access_token", "dummy.token.value")
        self.assertIsNone(result, "Seharusnya None jika token sudah expired.")

    @patch('sso_ui.token.UntypedToken')
    def test_decode_token_non_expired_claim(self, mock_untypedtoken):
        """
        Menguji jika 'exp' pada claims masih valid (exp_time >= now).
        """
        valid_claims = {
            "exp": int(timezone.now().timestamp()) + 100, # waktu di masa depan
            "role": "pengguna",                           # role valid
            "organization": "Ilmu Komputer",              # organisasi valid
            "username": "testuser"
        }
        mock_instance = MagicMock()
        mock_instance.payload = valid_claims
        mock_untypedtoken.return_value = mock_instance

        result = decode_token(self.config, "access_token", "dummy.token.value")
        self.assertIsNotNone(result, "Seharusnya tidak None jika token belum expired.")
        self.assertEqual(result["username"], "testuser")    

    ### UTILITAS ###
    
    def _generate_token(self, token_type, role, expired=False, offset=600):
        """
        Membuat token JWT valid atau expired menggunakan SimpleJWT.
        offset = selisih waktu (dlm detik) dari sekarang.
        """
        if token_type == "access_token":
            token = AccessToken()
        elif token_type == "refresh_token":
            token = RefreshToken()
        else:
            raise ValueError("Invalid token type")
        token["username"] = "testuser"
        token["role"] = role
        token["organization"] = "Ilmu Komputer"
        if expired:
            # Override klaim "exp" agar berada di masa lalu
            token["exp"] = int(timezone.now().timestamp() - offset)
        else:
            token["exp"] = int(timezone.now().timestamp() + offset)
        return str(token)

    def _decode_token(self, token_type, token):
        """Fungsi utilitas untuk mendekode token JWT."""
        return decode_token(self.config, token_type, token)

class TicketValidationTest(unittest.TestCase):
    def setUp(self):
        self.config = SSOJWTConfig()

    @patch("sso_ui.ticket.requests.get")
    def test_validate_ticket_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">
            <cas:authenticationSuccess>
                <cas:user>testuser</cas:user>
                <cas:attributes>
                    <cas:ldap_cn>Test User</cas:ldap_cn>
                    <cas:kd_org>01.00.12.01</cas:kd_org>
                    <cas:peran_user>mahasiswa</cas:peran_user>
                    <cas:nama>Test User</cas:nama>
                    <cas:npm>12345678</cas:npm>
                </cas:attributes>
            </cas:authenticationSuccess>
        </cas:serviceResponse>"""
        mock_get.return_value = mock_response

        result = validate_ticket(self.config, "valid_ticket")
        self.assertEqual(result["authentication_success"]["user"], "testuser")
        self.assertEqual(result["authentication_success"]["attributes"]["nama"], "Test User")
        self.assertEqual(result["authentication_success"]["attributes"]["npm"], "12345678")
        self.assertEqual(result["authentication_success"]["attributes"]["kd_org"], "01.00.12.01")
        self.assertEqual(result["authentication_success"]["attributes"]["peran_user"], "mahasiswa")

    @patch("sso_ui.ticket.requests.get")
    def test_validate_ticket_invalid_ticket(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">
            <cas:authenticationFailure code="INVALID_TICKET">
                Ticket not recognized
            </cas:authenticationFailure>
        </cas:serviceResponse>"""
        mock_get.return_value = mock_response

        with self.assertRaises(ValidateTicketError) as context:
            validate_ticket(self.config, "invalid_ticket")

        self.assertEqual(str(context.exception), "AuthenticationFailed")

    @patch("sso_ui.ticket.requests.get")
    def test_validate_ticket_xml_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """<invalid>"""
        mock_get.return_value = mock_response

        with self.assertRaises(ValidateTicketError) as context:
            validate_ticket(self.config, "invalid_xml")

        self.assertEqual(str(context.exception), "XMLParsingError")

    @patch("sso_ui.ticket.requests.get")
    def test_validate_ticket_request_error(self, mock_get):
        mock_get.side_effect = requests.RequestException("Request failed")

        with self.assertRaises(ValidateTicketError) as context:
            validate_ticket(self.config, "request_error")

        self.assertEqual(str(context.exception), "RequestError")
    
    @patch("sso_ui.ticket.requests.get")
    def test_validate_ticket_missing_user(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">
            <cas:authenticationSuccess>
                <cas:attributes>
                    <cas:kd_org>01.00.12.01</cas:kd_org>
                    <cas:peran_user>mahasiswa</cas:peran_user>
                    <cas:nama>Test User</cas:nama>
                    <cas:npm>12345678</cas:npm>
                </cas:attributes>
            </cas:authenticationSuccess>
        </cas:serviceResponse>"""

        mock_get.return_value = mock_response

        with self.assertRaises(ValidateTicketError) as context:
            validate_ticket(self.config, "missing_user")

        self.assertEqual(str(context.exception), "XMLParsingError")

    @patch("sso_ui.ticket.requests.get")
    def test_validate_ticket_missing_attributes(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">
            <cas:authenticationSuccess>
                <cas:user>testuser</cas:user>
            </cas:authenticationSuccess>
        </cas:serviceResponse>"""

        mock_get.return_value = mock_response

        with self.assertRaises(ValidateTicketError) as context:
            validate_ticket(self.config, "missing_attributes")

        self.assertEqual(str(context.exception), "XMLParsingError")

class OrganizationTest(unittest.TestCase):
    def test_get_organizations_valid_json(self):
        orgs = get_organizations()
        self.assertIsInstance(orgs, dict)
        self.assertIn("01.00.12.01", orgs)
        self.assertEqual(orgs["01.00.12.01"]["faculty"], "Ilmu Komputer")

    @patch("builtins.open", new_callable=mock_open, read_data="invalid_json")
    def test_get_organizations_invalid_json(self, mock_file):
        orgs = get_organizations()
        self.assertEqual(orgs, {})

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_get_organizations_file_not_found(self, mock_file):
        orgs = get_organizations()
        self.assertEqual(orgs, {}) 

    def test_get_organization_valid_code(self):
        org_data = get_organization("01.00.12.01")
        self.assertIsNotNone(org_data)
        self.assertEqual(org_data["faculty"], "Ilmu Komputer")

    def test_get_organization_invalid_code(self):
        org_data = get_organization("99.99.99.99")
        self.assertIsNone(org_data)