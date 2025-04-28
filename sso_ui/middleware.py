# middleware.py
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip authentication for public paths
        if request.path in ['/login/', '/cas/callback/']:
            return self.get_response(request)
            
        auth = JWTAuthentication()
        try:
            header = auth.get_header(request)
            if header:
                raw_token = auth.get_raw_token(header)
                validated_token = auth.get_validated_token(raw_token)
                request.user = auth.get_user(validated_token)
        except InvalidToken:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        
        return self.get_response(request)