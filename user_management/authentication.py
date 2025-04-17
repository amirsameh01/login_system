from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from user_management.models import User

class PhoneTokenAuthentication(TokenAuthentication):
    keyword = 'Token'

    def authenticate_credentials(self, key):
        try:
            user = User.objects.get(auth_token=key)
        except User.DoesNotExist:
            raise AuthenticationFailed('Invalid token')
        
        if not user.is_active:
            raise AuthenticationFailed('User inactive or deleted')
            
        return (user, key)