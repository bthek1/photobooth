#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Stopping Gunicorn service..."
sudo systemctl stop gunicorn

echo "Disabling Gunicorn service..."
sudo systemctl disable gunicorn

echo "Removing Gunicorn service file..."
sudo rm /etc/systemd/system/gunicorn.service

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Uninstalling Gunicorn..."
poetry remove gunicorn

echo "Gunicorn uninstalled successfully."
