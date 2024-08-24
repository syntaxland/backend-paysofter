# sellers/models.py 
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

BUSINESS_TYPE_CHOICES = [
        ('Registered', 'Registered'), 
        ('Unregistered', 'Unregistered'), 
    ]

STAFF_SIZE_CHOICES = [
        ('Small', 'Small (1-50 employees)'),
        ('Medium', 'Medium (51-250 employees)'), 
        ('Large', 'Large (251+ employees)'),
    ]

BUSINESS_INDUSTRY_CHOICES = [
        ('Information Technology', 'Information Technology'),
        ('Healthcare', 'Healthcare'),
        ('Finance', 'Finance'),
        ('Education', 'Education'),
        ('Retail', 'Retail'),
        ('Manufacturing', 'Manufacturing'),
        ('Services', 'Services'),
        ('Entertainment', 'Entertainment'),
        ('Food', 'Food & Beverage'),
        ('Travel', 'Travel & Tourism'),
        ('Real Estate', 'Real Estate'),
        ('Construction', 'Construction'),
        ('Automotive', 'Automotive'),
        ('Agriculture', 'Agriculture'),
        ('Energy', 'Energy'),
        ('Environmental', 'Environmental'),
        ('Government', 'Government'),
        ('Nonprofit', 'Nonprofit'),
        ('Others', 'Others'),
    ]

BUSINESS_CATEGORY_CHOICES = [
  ('Startup', 'Startup'),
  ('Small Business', 'Small Business'),
  ('Medium Business', 'Medium Business'),
  ('Large Business', 'Large Business'),
  ('Corporation', 'Corporation'),
  ('Sole Proprietorship', 'Sole Proprietorship'),
  ('Partnership', 'Partnership'),
  ('Franchise', 'Franchise'),
  ('Family Owned', 'Family Owned'),
  ('Online Business', 'Online Business'),
  ('Brick and Mortar', 'Brick and Mortar'),
  ('Service Provider', 'Service Provider'),
  ('Retailer', 'Retailer'),
  ('Wholesaler', 'Wholesaler'),
  ('Manufacturer', 'Manufacturer'),
  ('Restaurant', 'Restaurant'),
  ('Hospitality', 'Hospitality'),
  ('Healthcare', 'Healthcare'),
  ('Education', 'Education'),
  ('Tech', 'Tech'),
  ('Creative', 'Creative'),
  ('Entertainment', 'Entertainment'),
  ('Travel', 'Travel'),
  ('Construction', 'Construction'),
  ('Automotive', 'Automotive'),
  ('Agriculture', 'Agriculture'),
  ('Energy', 'Energy'),
  ('Environmental', 'Environmental'),
  ('Government', 'Government'),
  ('Nonprofit', 'Nonprofit'),
  ('Others', 'Others'),
]

ID_TYPE_CHOICES = [
        ('NIN', 'NIN'),
        ('Intl Passport', 'Intl Passport'), 
        ('Driving License', 'Driving License'),
        ('Govt Issued ID', 'Govt Issued ID'),
    ]


class SellerAccount(models.Model):
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="seller_account_user")
    business_name = models.CharField(max_length=100, null=True)
    trading_name = models.CharField(max_length=100, null=True, blank=True)
    # is_business_registered = models.BooleanField(default=False)
    business_reg_num = models.CharField(max_length=50, null=True, blank=True)
    # business_reg_cert = models.ImageField(upload_to='media/sellers/', null=True, blank=True)
    business_address = models.CharField(max_length=225, null=True)
    business_type = models.CharField(max_length=225, null=True, choices=BUSINESS_TYPE_CHOICES)
    staff_size = models.CharField( max_length=50, null=True, choices=STAFF_SIZE_CHOICES)
    business_industry = models.CharField( max_length=50, null=True, choices=BUSINESS_INDUSTRY_CHOICES)    
    business_category = models.CharField( max_length=50, null=True, choices=BUSINESS_CATEGORY_CHOICES)
    business_description = models.TextField(max_length=225, null=True, blank=True)
    business_phone = models.CharField(max_length=225, null=True, blank=True)
    business_email = models.CharField(max_length=225, null=True, blank=True)
    support_email = models.CharField(max_length=225, null=True, blank=True) 
    business_website = models.CharField(max_length=225, null=True, blank=True)
    country = models.CharField(max_length=225, null=True, blank=True)
    business_logo = models.ImageField(upload_to='media/sellers/', null=True, blank=True)
    # is_seller_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="seller_verified_by")
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.business_name}"


class BusinessStatus(models.Model):
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="business_status_user")
    is_business_registered = models.BooleanField(default=False)
    business_status = models.CharField(max_length=225, null=True, choices=BUSINESS_TYPE_CHOICES, default="Unregistered")
    business_name = models.CharField(max_length=100, null=True, blank=True)
    business_reg_num = models.CharField(max_length=50, null=True, blank=True)
    business_reg_cert = models.ImageField(upload_to='media/sellers/', null=True, blank=True)
    is_business_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)


class BusinessOwnerDetail(models.Model):
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="business_owner_user")
    director_name = models.CharField(max_length=225, null=True, blank=True)
    id_type = models.CharField( max_length=50, null=True, blank=True, choices=ID_TYPE_CHOICES)    
    id_number = models.CharField(max_length=30, null=True)
    id_card_image = models.ImageField(upload_to='media/sellers/')
    dob = models.CharField(max_length=225, null=True, blank=True)
    address = models.CharField(max_length=225, null=True, blank=True)
    proof_of_address = models.ImageField(upload_to='media/sellers/')
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.director_name}"


class BankAccount(models.Model):
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="seller_bank_account") 
    account_name = models.CharField(max_length=100,  null=True)
    bank_account_number = models.CharField(max_length=10,  null=True)
    bank_name = models.CharField(max_length=100,  null=True)
    is_bank_account_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True,  null=True) 

    def __str__(self):
        return f"{self.seller}"


class UsdBankAccount(models.Model):
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="seller_usd_bank_account") 
    account_name = models.CharField(max_length=100,  null=True)
    bank_account_number = models.CharField(max_length=10,  null=True)
    bank_name = models.CharField(max_length=100,  null=True)
    is_usd_bank_account_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True,  null=True) 

    def __str__(self):
        return f"{self.seller}"

 
class BankVerificationNumber(models.Model):
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="bvn_seller") 
    bvn = models.CharField(max_length=10, null=True)
    is_bvn_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True,  null=True) 

    def __str__(self):
        return f"{self.seller}"


class SellerPhoto(models.Model):
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="photo_seller")   
    photo = models.ImageField(upload_to='media/sellers/')
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f'Photo {self.pk}'
 