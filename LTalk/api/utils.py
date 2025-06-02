import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

security_logger = logging.getLogger('security')

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Log security-related exceptions
    request = context.get('request')
    if request:
        # Extract these for use in the log message
        username = request.user.username if hasattr(request.user, 'username') and request.user.is_authenticated else 'anonymous'
        ip_address = request.META.get('REMOTE_ADDR', 'unknown')
        
        # Use extra parameter to provide variables for formatter
        security_logger.warning(
            f"API Exception: {exc} - Path: {request.path} - Method: {request.method}",
            extra={
                'remote_addr': ip_address,
                'user': username
            }
        )
        
    if response is not None:
        if response.status_code == 403:
            response.data['detail'] = "You don't have permission to perform this action."
        
    return response