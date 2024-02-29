#!/usr/bin/env bash

# sudo apt install -y python3-pip
# sudo apt install -y nginx
# sudo apt install -y virtualenv

sudo apt-get update 
sudo apt-get install libmysqlclient-dev python3-dev 
sudo apt-get install redis-server 
sudo systemctl enable redis-server.service 
sudo apt-get install supervisor 
