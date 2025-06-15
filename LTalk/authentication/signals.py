from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login
import logging

auth_logger = logging.getLogger('authentication')

@receiver(pre_social_login)
def handle_social_login(sender, request, sociallogin, **kwargs):
    """
    Handle user data after successful social login
    """
    user = sociallogin.user
    
    # Log the social login attempt
    auth_logger.info(f"Social login: {user.email} via {sociallogin.account.provider}")
    
    # Set user settings/preferences if this is a new user
    if not user.id:
        auth_logger.info(f"New user created via {sociallogin.account.provider}: {user.email}")
        
        # Set default language based on browser or provider data
        user.language = 'en'  # Default language
        
        # Extract more data from Google account
        if sociallogin.account.provider == 'google':
            extra_data = sociallogin.account.extra_data
            
            # Set username if not provided (use part of email or name from Google)
            if not user.username and 'name' in extra_data:
                user.username = extra_data.get('name').split()[0]
            elif not user.username:
                user.username = user.email.split('@')[0]
            
            # Set language preference based on Google locale
            if 'locale' in extra_data:
                google_locale = extra_data['locale'][:2]  # Take first two chars
                if google_locale in ['en', 'ru', 'uk']:
                    user.language = google_locale