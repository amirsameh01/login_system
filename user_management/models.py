from django.db import models

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class User(AbstractUser):
    username = None
    phone_number = models.CharField(max_length=15, unique=True,  # assuming to ignore country code.
                                     validators=[RegexValidator(regex=r'^\d+$', message="Phone number must contain only digits")])

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []


