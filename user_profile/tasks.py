# user_profile/tasks.py
import random
import string

from celery import shared_task
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_security_code():
    return ''.join(random.choices(string.digits, k=4))


@shared_task
def update_security_codes_for_users():
    users = User.objects.all()
    
    for user in users:
        new_security_code = generate_security_code()
        
        user.security_code = new_security_code
        user.save()

    print("Security codes updated for all users.")


 
"""
celery -A core.celery worker --pool=solo -l info 
(Windows)
celery -A core.celery worker --loglevel=info (Unix) 
celery -A core.celery beat --loglevel=info 
"""
 