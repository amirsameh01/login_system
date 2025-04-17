from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
import random 
from user_management.decorators import check_block_status, get_client_ip
from user_management.serializers import PhoneNumberSerializer, UserProfileSerializer
from django.utils.decorators import method_decorator
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from user_management.authentication import PhoneTokenAuthentication
from user_management.utils import increase_failed_attempts_count, apply_block, reset_failed_attempts_count

User = get_user_model()



class CheckUserStateView(APIView):

    @method_decorator(check_block_status)
    def generate_and_cache_otp(self, request):
        """ generate and cache otp. returns a random 6 digit otp"""
        phone_number = request.data.get('phone_number')
        otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        otp_key = f"otp_{phone_number}"
        cache.set(otp_key, otp_code, timeout=5*60)
        return otp_code

    def post(self, request, *args, **kwargs):
        """
        user phone number validation and otp generation.
         
        payload:
            phone_number: (str) in iranian valid format
        
        returns:
            user existance state
            custom code & next_page as front end side navigation hints :)
            otp code for new users
        """
        serializer = PhoneNumberSerializer(data=request.data)
            
        try:
            serializer.is_valid(raise_exception=True)
            validated_phone = serializer.validated_data['phone_number']
            
            is_exists = User.objects.filter(phone_number=validated_phone).exists()
            
            if is_exists:
                return Response({
                    'exists': True,
                    'message': 'User with this phone number exists. please proceed to login.',
                    'custom_code': 1001,
                    'next_page': 'login'
                }, status=200)
            else:
                otp_code = self.generate_and_cache_otp(request)

                return Response({
                    'exists': False,
                    'message': 'otp sent(included in response for dev purposes). Please verify your phone number.',
                    'custom_code': 1002,
                    'next_page': 'verify_otp',
                    'otp': otp_code
                }, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        

class UserLoginView(APIView):
    
    @method_decorator(check_block_status)
    def post(self, request, *args, **kwargs):
        """
        user login system using phone_number and password

        returns:
            auth status
            auth token (on success)
            custom_code & next_page as front end side navigation hints
        """
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')

        try:
            user = User.objects.get(phone_number=phone_number)
            
            user = authenticate(request, phone_number=phone_number, password=password)
            if user:
                token, created = Token.objects.get_or_create(user=user)

                reset_failed_attempts_count(phone_number, 'phone_number')
                reset_failed_attempts_count(get_client_ip(request), 'ip_address')
                return Response({
                    'message': 'You have been successfully logged in',
                    'custom_code': 2001,
                    'auth_token': token.key,
                    'next_page': 'main'}, status=200)
            
            else:
                increase_failed_attempts_count(phone_number, 'phone_number')
                increase_failed_attempts_count(get_client_ip(request),'ip_address')
                return Response({
                    'message': 'Invalid credentials, please try again.',
                    'custom_code': 2002,
                    'next_page': 'login'}, status=400)

        except User.DoesNotExist: 
            increase_failed_attempts_count(phone_number, 'phone_number')
            increase_failed_attempts_count(get_client_ip(request),'ip_address')
            return Response({
                'message': 'User with this phone number does not exist.',
                'custom_code': 2003,
                'next_page': 'login'}, status=404)
        

class VerifyOtpView(APIView):

    @method_decorator(check_block_status)
    def post(self, request, *args, **kwargs):
        """
        verify otp for user registeration

        returns:
            login status
            auth token (on success)
            custom_code & next_page as front end side navigation hints
        """
        phone_number = request.data.get('phone_number')
        otp_code = str(request.data.get('otp_code'))


        valid_otp = cache.get(f'otp_{phone_number}')
        if otp_code and valid_otp and otp_code == valid_otp:
            user, created = User.objects.get_or_create(phone_number=phone_number)
            
            token = Token.objects.create(user=user)
            
            reset_failed_attempts_count(phone_number, 'phone_number')
            reset_failed_attempts_count(get_client_ip(request), 'ip_address')
            return Response({
                'message': 'You have been succesfully registered, please procced to complete your profile',
                'custom_code': 3001,
                'auth_token': token.key,
                'next_page': 'complete_profile'}, status=201)
        else:
            increase_failed_attempts_count(phone_number, 'phone_number')
            increase_failed_attempts_count(get_client_ip(request),'ip_address')            
            return Response({'message': 'Invalid OTP code, try again'}, status=401)
        
class CompleteProfileView(APIView):
    
    authentication_classes = [PhoneTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def put(self, request, *args, **kwargs):
        """
        complete/Update user profile after initial registration.
    
        Returns:
            profile update status
            success/error message
        """
        serializer = UserProfileSerializer(request.user, data=request.data)
    
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Profile updated successfully'
            })
        else:
            return Response({
                'status': 'error',
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=400)
