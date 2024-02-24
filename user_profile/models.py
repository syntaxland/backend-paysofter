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




CURRENCY_CHOICES = (
        ('NGN', 'Nigerian Naira'),
        ('USD', 'United States Dollar'),
        ('GBP', 'British Pound Sterling'),
        ('EUR', 'Euro'),  
        ('JPY', 'Japanese Yen'),
        ('CAD', 'Canadian Dollar'),
        ('AUD', 'Australian Dollar'),
        ('INR', 'Indian Rupee'),
        ('CNY', 'Chinese Yuan'),
        ('ZAR', 'South African Rand'),
        ('BRL', 'Brazilian Real'),
        ('KES', 'Kenyan Shilling'),
        ('GHS', 'Ghanaian Cedi'),
        ('AED', 'United Arab Emirates Dirham'),
        ('SAR', 'Saudi Riyal'),
        ('GBP', 'British Pound Sterling'),
    )

class User(AbstractBaseUser, PermissionsMixin):
    account_id = models.CharField(max_length=12, unique=True, null=True, editable=False)  
    security_code = models.CharField(max_length=4, unique=True, null=True, editable=False)  
    email = models.EmailField(max_length=100, unique=True, editable=False)
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    phone_number = models.CharField(max_length=18, unique=True)
    is_verified = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='images/avatars/', null=True, blank=True) 
    referral_code = models.CharField(max_length=10, unique=True, null=True, editable=False) 
    referral_link = models.CharField(max_length=225, unique=True, null=True, editable=False)
    test_api_key = models.CharField(max_length=100, unique=True, null=True, editable=False)
    test_api_secret_key = models.CharField(max_length=100, unique=True, null=True, editable=False)
    live_api_key = models.CharField(max_length=100, unique=True, null=True, editable=False)
    live_api_secret_key = models.CharField(max_length=100, unique=True, null=True, editable=False)
    is_api_key_live = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)  
    is_seller = models.BooleanField(default=False)
    is_usd_selected = models.BooleanField(default=False)
    selected_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD', null=True, blank=True)
    is_terms_conditions_read = models.BooleanField(default=False)

    user_is_not_active = models.BooleanField(default=False)  
    is_user_live_banned = models.BooleanField(default=False)  
    is_user_1day_banned = models.BooleanField(default=False)  
    is_user_2day_banned = models.BooleanField(default=False)  
    is_user_3day_banned = models.BooleanField(default=False)  
    is_user_1week_banned = models.BooleanField(default=False)  
    is_user_3week_banned = models.BooleanField(default=False)  
    is_user_1month_banned = models.BooleanField(default=False)  
    is_user_2month_banned = models.BooleanField(default=False)  
    is_user_3month_banned = models.BooleanField(default=False)  
    is_user_6month_banned = models.BooleanField(default=False)  
    is_user_1year_banned = models.BooleanField(default=False) 
    
    created_at = models.DateTimeField(default=timezone.now, blank=True) 
  
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'phone_number']

    def __str__(self):
        return f"{self.email}" 
 
    objects = CustomUserManager()

    class Meta: 
        default_related_name = 'user'
        # verbose_name = _('user')
