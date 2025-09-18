#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Stopping rm-server service..."
sudo systemctl stop rm-server

echo "Disabling rm-server service..."
sudo systemctl disable rm-server

echo "Removing rm-server service file..."
sudo rm /etc/systemd/system/rm-server.service

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "rm-server removed successfully."
