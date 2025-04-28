import json

def get_organizations():
    try:
        with open("sso_ui/orgs_code.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as _:
        return {}
    
def get_organization(org_code):
    orgs = get_organizations()
    return orgs.get(org_code)