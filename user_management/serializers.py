from rest_framework import serializers
from django.contrib.auth import get_user_model
from user_management.utils import validate_phone_number

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'password')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            # 'email': {'required': True}
        }
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
            
        instance.save()
        return instance
    
class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    
    def validate_phone_number(self, value):
        """
        Validate and normalize phone number
        """
        normalized_phone = validate_phone_number(value)
        
        if not normalized_phone:
            raise serializers.ValidationError(
                'Invalid phone number format. '
                'Expected 10 or 11 digits starting with 0.'
            )
        
        return normalized_phone