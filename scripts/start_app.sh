#!/usr/bin/bash 

sed -i 's/\[]/\["2-3-91-70-252"]/' /home/ubuntu/backend-paysofter/backend-paysofter/settings.py

python manage.py migrate 
python manage.py collectstatic
python manage.py migrate 
sudo service gunicorn restart
sudo service nginx restart

#sudo tail -f /var/log/nginx/error.log
#sudo systemctl reload nginx
#sudo nginx -t
#sudo systemctl restart gunicorn
#sudo systemctl status gunicorn
#sudo systemctl status nginx

# Check the status
#systemctl status gunicorn

# Restart:
#systemctl restart gunicorn
#sudo systemctl status nginx
