# user_profile/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# from django.utils.translation import gettext as _
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    def _create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    account_id = models.CharField(max_length=12, unique=True, null=True)  
    email = models.EmailField(max_length=100, unique=True)
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    phone_number = models.CharField(max_length=18, unique=True)
    is_verified = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='images/avatars/', null=True, blank=True) 
    referral_code = models.CharField(max_length=10, unique=True, null=True) 
    referral_link = models.CharField(max_length=225, unique=True, null=True)
    # referred_users = models.ManyToManyField('referral.Referral', related_name='referred_users')
    test_api_key = models.CharField(max_length=100, unique=True, null=True)
    test_api_secret_key = models.CharField(max_length=100, unique=True, null=True)
    live_api_key = models.CharField(max_length=100, unique=True, null=True)
    live_api_secret_key = models.CharField(max_length=100, unique=True, null=True)
    is_live_mode = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)  
    created_at = models.DateTimeField(default=timezone.now, blank=True)
  
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'phone_number']

    def save(self, *args, **kwargs):
        self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
 
    objects = CustomUserManager()

    class Meta: 
        default_related_name = 'user'
        # verbose_name = _('user')
