# promise/models.py
from datetime import timedelta, datetime
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

CURRENCY_CHOICES = (
    ('NGN', 'NGN'),
    ('USD', 'USD'),
    ('CAD', 'CAD'),
    ('EUR', 'EUR'),
    ('GBP', 'GBP'),
    ('GHS', 'GHS'),
    ('INR', 'INR'),
    ('CNY', 'CNY'),
    ('ZAR', 'ZAR'),
    ('AED', 'United Arab Emirates Dirham'),
    ('AUD', 'Australian Dollar'),
    ('BRL', 'Brazilian Real'),
    ('JPY', 'Japanese Yen'),
    ('KES', 'Kenyan Shilling'),
    ('SAR', 'Saudi Riyal'),
    # Additional currencies sorted alphabetically
    ('AFN', 'Afghan Afghani'),
    ('ALL', 'Albanian Lek'),
    ('AMD', 'Armenian Dram'),
    ('ANG', 'Netherlands Antillean Guilder'),
    ('AOA', 'Angolan Kwanza'),
    ('ARS', 'Argentine Peso'),
    ('AWG', 'Aruban Florin'),
    ('AZN', 'Azerbaijani Manat'),
    ('BAM', 'Bosnia-Herzegovina Convertible Mark'),
    ('BBD', 'Barbadian Dollar'),
    ('BDT', 'Bangladeshi Taka'),
    ('BGN', 'Bulgarian Lev'),
    ('BHD', 'Bahraini Dinar'),
    ('BIF', 'Burundian Franc'),
    ('BMD', 'Bermudian Dollar'),
    ('BND', 'Brunei Dollar'),
    ('BOB', 'Bolivian Boliviano'),
    ('BSD', 'Bahamian Dollar'),
    ('BTN', 'Bhutanese Ngultrum'),
    ('BWP', 'Botswanan Pula'),
    ('BYN', 'Belarusian Ruble'),
    ('BZD', 'Belize Dollar'),
    ('CDF', 'Congolese Franc'),
    ('CHF', 'Swiss Franc'),
    ('CLP', 'Chilean Peso'),
    ('COP', 'Colombian Peso'),
    ('CRC', 'Costa Rican Colón'),
    ('CUP', 'Cuban Peso'),
    ('CVE', 'Cape Verdean Escudo'),
    ('CZK', 'Czech Republic Koruna'),
    ('DJF', 'Djiboutian Franc'),
    ('DKK', 'Danish Krone'),
    ('DOP', 'Dominican Peso'),
    ('DZD', 'Algerian Dinar'),
    ('EGP', 'Egyptian Pound'),
    ('ERN', 'Eritrean Nakfa'),
    ('ETB', 'Ethiopian Birr'),
    ('FJD', 'Fijian Dollar'),
    ('FKP', 'Falkland Islands Pound'),
    ('FOK', 'Faroe Islands Króna'),
    ('GEL', 'Georgian Lari'),
    ('GGP', 'Guernsey Pound'),
    ('GIP', 'Gibraltar Pound'),
    ('GMD', 'Gambian Dalasi'),
    ('GNF', 'Guinean Franc'),
    ('GTQ', 'Guatemalan Quetzal'),
    ('GYD', 'Guyanaese Dollar'),
    ('HKD', 'Hong Kong Dollar'),
    ('HNL', 'Honduran Lempira'),
    ('HRK', 'Croatian Kuna'),
    ('HTG', 'Haitian Gourde'),
    ('HUF', 'Hungarian Forint'),
    ('IDR', 'Indonesian Rupiah'),
    ('ILS', 'Israeli New Shekel'),
    ('IMP', 'Isle of Man Pound'),
    ('IQD', 'Iraqi Dinar'),
    ('IRR', 'Iranian Rial'),
    ('ISK', 'Icelandic Króna'),
    ('JEP', 'Jersey Pound'),
    ('JMD', 'Jamaican Dollar'),
    ('JOD', 'Jordanian Dinar'),
    ('KGS', 'Kyrgystani Som'),
    ('KHR', 'Cambodian Riel'),
    ('KID', 'Kiribati Dollar'),
    ('KWD', 'Kuwaiti Dinar'),
    ('KYD', 'Cayman Islands Dollar'),
    ('KZT', 'Kazakhstani Tenge'),
    ('LAK', 'Laotian Kip'),
    ('LBP', 'Lebanese Pound'),
    ('LKR', 'Sri Lankan Rupee'),
    ('LRD', 'Liberian Dollar'),
    ('LSL', 'Lesotho Loti'),
    ('LYD', 'Libyan Dinar'),
    ('MAD', 'Moroccan Dirham'),
    ('MDL', 'Moldovan Leu'),
    ('MGA', 'Malagasy Ariary'),
    ('MKD', 'Macedonian Denar'),
    ('MMK', 'Myanma Kyat'),
    ('MNT', 'Mongolian Tugrik'),
    ('MOP', 'Macanese Pataca'),
    ('MRU', 'Mauritanian Ouguiya'),
    ('MUR', 'Mauritian Rupee'),
    ('MVR', 'Maldivian Rufiyaa'),
    ('MWK', 'Malawian Kwacha'),
    ('MXN', 'Mexican Peso'),
    ('MYR', 'Malaysian Ringgit'),
    ('MZN', 'Mozambican Metical'),
    ('NAD', 'Namibian Dollar'),
    ('NIO', 'Nicaraguan Córdoba'),
    ('NOK', 'Norwegian Krone'),
    ('NPR', 'Nepalese Rupee'),
    ('NZD', 'New Zealand Dollar'),
    ('OMR', 'Omani Rial'),
    ('PAB', 'Panamanian Balboa'),
    ('PEN', 'Peruvian Nuevo Sol'),
    ('PGK', 'Papua New Guinean Kina'),
    ('PHP', 'Philippine Peso'),
    ('PKR', 'Pakistani Rupee'),
    ('PLN', 'Polish Złoty'),
    ('PYG', 'Paraguayan Guarani'),
    ('QAR', 'Qatari Rial'),
    ('RON', 'Romanian Leu'),
    ('RSD', 'Serbian Dinar'),
    ('RUB', 'Russian Ruble'),
    ('RWF', 'Rwandan Franc'),
    ('SBD', 'Solomon Islands Dollar'),
    ('SCR', 'Seychellois Rupee'),
    ('SDG', 'Sudanese Pound'),
    ('SEK', 'Swedish Krona'),
    ('SGD', 'Singapore Dollar'),
    ('SHP', 'Saint Helena Pound'),
    ('SLL', 'Sierra Leonean Leone'),
    ('SOS', 'Somali Shilling'),
    ('SRD', 'Surinamese Dollar'),
    ('SSP', 'South Sudanese Pound'),
    ('STN', 'São Tomé and Príncipe Dobra'),
    ('SYP', 'Syrian Pound'),
    ('SZL', 'Swazi Lilangeni'),
    ('TJS', 'Tajikistani Somoni'),
    ('TMT', 'Turkmenistani Manat'),
    ('TND', 'Tunisian Dinar'),
    ('TOP', 'Tongan Paʻanga'),
    ('TRY', 'Turkish Lira'),
    ('TTD', 'Trinidad and Tobago Dollar'),
    ('TVD', 'Tuvaluan Dollar'),
    ('TWD', 'New Taiwan Dollar'),
    ('TZS', 'Tanzanian Shilling'),
    ('UAH', 'Ukrainian Hryvnia'),
    ('UGX', 'Ugandan Shilling'),
    ('UYU', 'Uruguayan Peso'),
    ('UZS', 'Uzbekistan Som'),
    ('VES', 'Venezuelan Bolívar'),
    ('VND', 'Vietnamese Đồng'),
    ('VUV', 'Vanuatu Vatu'),
    ('WST', 'Samoan Tala'),
    ('XAF', 'Central African CFA Franc'),
    ('XCD', 'Eastern Caribbean Dollar'),
    ('XDR', 'Special Drawing Rights'),
    ('XOF', 'West African CFA franc'),
    ('XPF', 'CFP Franc'),
    ('YER', 'Yemeni Rial'),
    ('ZMW', 'Zambian Kwacha'),
)


PAYMENT_METHOD_CHOICES = (
        ('Debit Card', 'Debit Card'),
        ('Paysofter Account Fund', 'Paysofter Account Fund'),
        ('Paysofter Promise', 'Paysofter Promise'),
        ('Bank', 'Bank'),
        ('Transfer', 'Transfer'),
        ('QR COde', 'QR COde'),
        ('USSD', 'USSD'),
    )

PAYMENT_PROVIDER_CHOICES = (
        ('Paysofter', 'Paysofter'),
        ('Mastercard', 'Mastercard'),
        ('Verve', 'Verve'),
        ('Visa', 'Visa'),
        ('GTB', 'GTB'),
        ('Fidelity', 'Fidelity'),
    )

PROMISE_DURATION_CHOICES = (
        ('0 day', '0 day'),
        ('Within 1 day', 'Within 1 day'),
        ('2 days', 'Less than 2 days'),
        ('3 days', 'Less than 3 days'),
        ('5 days', 'Less than 5 days'),
        ('1 week', 'Less than 1 week'),
        ('2 weeks', 'Less than 2 weeks'),
        ('1 month', 'Less than 1 month'),
    )

PROMISE_STATUS_CHOICES = (
        ('Processing', 'Processing'),
        ('Fulfilled', 'Fulfilled'),
        ('Failed', 'Failed'),
        ('Cancelled', 'Cancelled'),
    )

class PaysofterPromise(models.Model):
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="promise_seller")
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="promise_payer")
    amount = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True, editable=False)
    currency = models.CharField(max_length=50, choices=CURRENCY_CHOICES, default='NGN', null=True, blank=True)
    duration = models.CharField(max_length=100, choices=PROMISE_DURATION_CHOICES, default='Within 1 day', null=True, blank=True)
    duration_hours = models.DurationField(null=True, blank=True)
    expiration_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=100, choices=PROMISE_STATUS_CHOICES, default='Processing', null=True, blank=True)
    is_success = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    buyer_promise_fulfilled = models.BooleanField(default=False)
    seller_fulfilled_promise = models.BooleanField(default=False)
    is_settle_conflict_activated = models.BooleanField(default=False)
    settle_conflict_charges = models.DecimalField(max_digits=16, decimal_places=2, default=0, null=True, blank=True, editable=False)
    service_charge = models.DecimalField(max_digits=16, decimal_places=2, default=0, null=True, blank=True, editable=False)
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True, default='Paysofter Promise')
    payment_provider = models.CharField(max_length=100, choices=PAYMENT_PROVIDER_CHOICES, default='Paysofter')
    promise_id = models.CharField(max_length=10, unique=True, null=True, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True) 

    def save(self, *args, **kwargs):
        if self.duration:
            if self.duration == '0 day':
                self.duration_hours = timedelta(hours=0)
            elif self.duration == 'Within 1 day':
                self.duration_hours = timedelta(hours=24)
            elif self.duration == '2 days':
                self.duration_hours = timedelta(days=2)
            elif self.duration == '3 days':
                self.duration_hours = timedelta(days=3)
            elif self.duration == '5 days':
                self.duration_hours = timedelta(days=5)
            elif self.duration == '1 week':
                self.duration_hours = timedelta(weeks=1)
            elif self.duration == '2 weeks':
                self.duration_hours = timedelta(weeks=2)
            elif self.duration == '1 month':
                self.duration_hours = timedelta(days=30)  

            self.expiration_date = datetime.now() + self.duration_hours
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.promise_id}" 
    

class PromiseMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="promise_message_user")
    promise_message = models.ForeignKey(PaysofterPromise, on_delete=models.CASCADE, related_name='promise_message', blank=True, null=True)
    message = models.TextField(max_length=225, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self): 
        return f"{self.user} | {self.promise_message}" 
