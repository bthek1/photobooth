#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Stopping Nginx..."
sudo systemctl stop nginx

echo "Uninstalling Nginx..."
sudo apt remove --purge -y nginx nginx-common nginx-full

echo "Removing Nginx configuration and log files..."
sudo rm -rf /etc/nginx
sudo rm -rf /var/www/html
sudo rm -rf /var/log/nginx
sudo rm -rf /usr/sbin/nginx
sudo rm -rf /usr/share/nginx

echo "Performing autoremove..."
sudo apt autoremove -y

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Nginx uninstalled successfully."
