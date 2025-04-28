import requests
import xml.etree.ElementTree as ET

class ValidateTicketError(Exception):
    pass

def validate_ticket(config, ticket):
    url = f"{config.cas_url}/serviceValidate?ticket={ticket}&service={config.service_url}"
    headers = {"User-Agent": "Python-Requests"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ValidateTicketError("RequestError") from e

    content = response.text
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        raise ValidateTicketError("XMLParsingError") from e

    ns = {'cas': 'http://www.yale.edu/tp/cas'}
    auth_success = root.find('.//cas:authenticationSuccess', ns)
    if auth_success is None:
        raise ValidateTicketError("AuthenticationFailed")
    
    user = auth_success.find('cas:user', ns)
    attributes = auth_success.find('cas:attributes', ns)
    if user is None or attributes is None:
        raise ValidateTicketError("XMLParsingError")
    
    def get_text(tag):
        elem = attributes.find(f'cas:{tag}', ns)
        return elem.text if elem is not None else ""
    
    user_data = {
        "user": user.text,
        "attributes": {
            "ldap_cn": get_text("ldap_cn"),
            "kd_org": get_text("kd_org"),
            "peran_user": get_text("peran_user"),
            "nama": get_text("nama"),
            "npm": get_text("npm")
        }
    }
    return {"authentication_success": user_data}