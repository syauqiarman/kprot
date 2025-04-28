import jwt
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from django.conf import settings
from .config import SSOJWTConfig

def create_token(user_data, token_type="access"):
    config = SSOJWTConfig()
    secret_key = (
        config.access_token_secret_key
        if token_type == "access"
        else config.refresh_token_secret_key
    )
    exp_time = (
        config.access_token_exp_time
        if token_type == "access"
        else config.refresh_token_exp_time
    )

    payload = {
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(seconds=exp_time),
        "username": user_data.get("username"),
        "nama": user_data.get("nama"),
        "npm": user_data.get("npm"),
        "organization": user_data.get("organization"),
    }

    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

def decode_token(token, token_type="access"):
    config = SSOJWTConfig()
    secret_key = (
        config.access_token_secret_key
        if token_type == "access"
        else config.refresh_token_secret_key
    )

    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Token invalid

def validate_ticket(ticket):
    config = SSOJWTConfig() 
    validation_url = f"{config.cas_url}/serviceValidate?ticket={ticket}&service={config.service_url}"

    try:
        response = requests.get(validation_url)
        response.raise_for_status()
    except requests.RequestException:
        return None 

    try:
        root = ET.fromstring(response.text)
    except ET.ParseError:
        return None  

    ns = {'cas': 'http://www.yale.edu/tp/cas'}
    auth_success = root.find('.//cas:authenticationSuccess', ns)
    if auth_success is None:
        return None

    user_elem = auth_success.find('cas:user', ns)
    if user_elem is None or not user_elem.text:
        return None

    attributes = auth_success.find('cas:attributes', ns)
    user_data = {"username": user_elem.text}
    if attributes is not None:
        for child in attributes:
            tag = child.tag.split('}')[-1]  # Menghilangkan namespace
            user_data[tag] = child.text

    return user_data
