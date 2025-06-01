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
        user_info = f"User: {request.user}" if request.user.is_authenticated else "Anonymous"
        path_info = f"Path: {request.path}"
        method_info = f"Method: {request.method}"
        ip_info = f"IP: {request.META.get('REMOTE_ADDR')}"
        
        security_logger.warning(
            f"API Exception: {exc} - {user_info} - {path_info} - {method_info} - {ip_info}"
        )
    
    # Add custom responses or modify existing ones
    if response is not None:
        if response.status_code == 403:
            response.data['detail'] = "You don't have permission to perform this action."
        
    return response