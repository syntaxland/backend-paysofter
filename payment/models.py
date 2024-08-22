# payment/models.py
from django.db import models
import os
import sys
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files import File
from PIL import Image, ImageDraw
import qrcode
from django.contrib.auth import get_user_model
from payout.models import Payout

User = get_user_model()  


class PaymentLink(models.Model):
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="payment_link_seller")
    buyer_name = models.CharField(max_length=225, null=True, blank=True) 
    buyer_email = models.CharField(max_length=225, null=True, blank=True) 
    buyer_phone = models.CharField(max_length=225, null=True, blank=True) 
    payment_name = models.CharField(max_length=225, null=True, blank=True) 
    payment_link = models.CharField(max_length=225, unique=True, null=True)
    payment_image = models.ImageField(upload_to='payment/img/', blank=True, null=True)
    payment_qrcode = models.ImageField(upload_to='payment/qr_codes/', blank=True, null=True)
    amount = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    currency = models.CharField(max_length=3, null=True, blank=True)
    description = models.TextField(max_length=1000, blank=True, null=True)
    show_promise_option = models.BooleanField(default=True)
    show_fund_option = models.BooleanField(default=False)
    show_card_option = models.BooleanField(default=False)
    show_buyer_name = models.BooleanField(default=False)
    show_buyer_phone = models.BooleanField(default=False)
    qty = models.PositiveIntegerField(default=1) 
    show_qty = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    payout_status = models.BooleanField(default=False) 
    is_success = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=50, unique=True, null=True)
    transaction_id = models.CharField(max_length=50, unique=True, null=True) 
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    payment_provider = models.CharField(max_length=50, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.qty < 1:
            self.qty = 1

        if self.payment_image and self.payment_name:
            img = Image.open(self.payment_image)
            img_name = self.payment_name
            extension = img.format.lower()
            thumbnail_size = (200, 200)
            img.thumbnail(thumbnail_size)
            thumb_io = BytesIO()
            img.save(thumb_io, format=extension)
            thumbnail_name = f"{img_name}_thumb.{extension}"
            self.payment_image = InMemoryUploadedFile(thumb_io, 'ImageField', thumbnail_name, f'image/{extension}', sys.getsizeof(thumb_io), None)

        super(PaymentLink, self).save(*args, **kwargs)

    def str(self):
        return f"{self.seller} - Payment Link: {self.payment_link}"

        # def save(self, *args, **kwargs):
    #     # If a payment link exists, generate QR code
    #     if self.payment_link:
    #         qr_code_img = qrcode.make(self.payment_link)
    #         canvas = Image.new('RGB', (290, 290), 'white')
    #         draw = ImageDraw.Draw(canvas)
    #         canvas.paste(qr_code_img)
    #         buffer = BytesIO()
    #         canvas.save(buffer, 'PNG')
    #         self.payment_qrcode.save(f'qr_code_{self.username}.png', File(buffer), save=False)
    #         canvas.close()
 

class PayoutPayment(models.Model):
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="payout_payment_seller") 
    payout = models.ForeignKey(Payout, on_delete=models.SET_NULL, null=True, blank=True, related_name="payout_payment")    
    
    bank_name = models.CharField(max_length=100)
    account_name = models.CharField(max_length=100)
    bank_account_number = models.CharField(max_length=10)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, editable=False)
    
    currency = models.CharField(max_length=3)  
    payment_method = models.CharField(max_length=50) 
    is_paid = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    payout_payment_id = models.CharField(max_length=10, unique=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seller} - {self.total_amount} - {self.payout_payment_id}"
