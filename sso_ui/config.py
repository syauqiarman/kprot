import os
from dotenv import load_dotenv

load_dotenv(override=True)

class SSOJWTConfig:
    def __init__(self):
        self.access_token_exp_time = int(os.getenv("ACCESS_TOKEN_EXP_TIME"))
        self.refresh_token_exp_time = int(os.getenv("REFRESH_TOKEN_EXP_TIME"))
        self.access_token_secret_key = os.getenv("ACCESS_TOKEN_SECRET_KEY")
        self.refresh_token_secret_key = os.getenv("REFRESH_TOKEN_SECRET_KEY")
        self.service_url = os.getenv("SERVICE_URL")
        self.origin_url = os.getenv("ORIGIN_URL")
        self.cas_url = os.getenv("CAS_URL")