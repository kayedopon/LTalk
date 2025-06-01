from django.utils import timezone
import re
import logging

security_logger = logging.getLogger('security')

class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        
        # Content Security Policy
        response['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;"
        
        # Additional security headers
        response['Permissions-Policy'] = "geolocation=(), microphone=(), camera=()"
        response['Cross-Origin-Opener-Policy'] = 'same-origin'
        response['Cross-Origin-Embedder-Policy'] = 'require-corp'
        
        return response

class AccessLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Log access before processing
        if request.user.is_authenticated:
            security_logger.info(f"Access: {request.user.email} - {request.method} {request.path} - {request.META.get('REMOTE_ADDR')}")
        else:
            security_logger.info(f"Anonymous access - {request.method} {request.path} - {request.META.get('REMOTE_ADDR')}")
            
        response = self.get_response(request)
        return response