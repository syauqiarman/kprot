import requests
import xml.etree.ElementTree as ET
from django.conf import settings

def validate_cas_ticket(ticket):
    cas_url = f"{settings.CAS_CONFIG['CAS_URL']}/serviceValidate"
    params = {
        'ticket': ticket,
        'service': settings.CAS_CONFIG['SERVICE_URL']
    }
    
    try:
        response = requests.get(cas_url, params=params)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        ns = {'cas': 'http://www.yale.edu/tp/cas'}
        
        if root.find('.//cas:authenticationFailure', ns) is not None:
            return None
            
        user_data = {
            'username': root.find('.//cas:user', ns).text,
            'attributes': {
                elem.tag.split('}')[1]: elem.text
                for elem in root.find('.//cas:attributes', ns)
            }
        }
        
        return user_data
    except Exception as e:
        return None