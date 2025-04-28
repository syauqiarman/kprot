from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, UntypedToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from sso_ui import orgs
from django.utils import timezone

VALID_ROLES = {"pengguna", "pengawas", "dosen", "koor_asdos"}

def create_token(config, token_type, service_response):
    user_attr = service_response.get("authentication_success")
    if not user_attr:
        raise Exception("Authentication failed: no user data")
    
    role = _determine_user_role(user_attr)
    custom_claims = {
        "username": user_attr.get("user"),
        "nama": user_attr.get("attributes", {}).get("nama"),
        "npm": user_attr.get("attributes", {}).get("npm"),
        "organization": _get_user_organization(user_attr),
        "role": role,
    }
    
    if token_type == "access_token":
        token = AccessToken()
        for key, value in custom_claims.items():
            token[key] = value
        return str(token)
    elif token_type == "refresh_token":
        token = RefreshToken()
        token["username"] = user_attr.get("user")
        token["role"] = role
        return str(token)
    else:
        raise ValueError("Invalid token type")

def decode_token(config, token_type, token):
    if token_type not in ["access_token", "refresh_token"]:
        raise ValueError("Invalid token type")
    try:
        untyped = UntypedToken(token)
        claims = untyped.payload  

        if "exp" in claims:
            exp_time = claims["exp"]
            if exp_time < timezone.now().timestamp():
                return None
            
        if claims.get("role") not in VALID_ROLES:
            return None
        
        organization = claims.get("organization")

        if isinstance(organization, dict):
            organization = organization.get("faculty")
        
        if not organization or organization != "Ilmu Komputer":
            return Response({"error": "Anda bukan bagian dari elemen Fasilkom UI!"}, status=401)

        return claims
    except TokenError:
        return None

### UTILITAS ###

def _determine_user_role(user_attr):
    peran_user = user_attr["attributes"].get("peran_user", "pengguna")
    return peran_user if peran_user in VALID_ROLES else _get_role_from_database(user_attr.get("user"))

def _get_role_from_database(username):
    User = get_user_model()
    try:
        user = User.objects.get(username=username)
        return user.role if user.role in VALID_ROLES else "pengguna"
    except User.DoesNotExist:
        return "pengguna"

def _get_user_organization(user_attr):
    kd_org = user_attr.get("attributes", {}).get("kd_org")
    return orgs.get_organization(kd_org)