#!/bin/bash

# Update system packages
echo "Updating system packages..."
sudo apt-get update -y

# Install Redis server
echo "Installing Redis..."
sudo apt-get install redis-server -y

# Configure Redis to start on system boot
echo "Enabling Redis to start on boot..."
sudo systemctl enable redis-server.service

# Start Redis server
echo "Starting Redis server..."
sudo systemctl start redis-server.service

# Check Redis server status
echo "Checking Redis server status..."
sudo systemctl status redis-server.service

# Output Redis version to verify installation
echo "Installed Redis version:"
redis-server --version

echo "Redis installation and setup complete!"
