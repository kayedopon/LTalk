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
        if hasattr(request, 'user') and request.user.is_authenticated:
            security_logger.info(
                "User access", 
                extra={
                    'remote_addr': request.META.get('REMOTE_ADDR', 'unknown'),
                    'user': request.user.username
                }
            )
        else:
            security_logger.info(
                "Anonymous access", 
                extra={
                    'remote_addr': request.META.get('REMOTE_ADDR', 'unknown'),
                    'user': 'anonymous'
                }
            )
        response = self.get_response(request)
        return response