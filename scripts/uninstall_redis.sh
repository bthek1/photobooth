#!/bin/bash

# Stop Redis service
echo "Stopping Redis service..."
sudo systemctl stop redis-server

# Disable Redis service from starting on boot
echo "Disabling Redis service from startup..."
sudo systemctl disable redis-server

# Uninstall Redis server
echo "Uninstalling Redis..."
sudo apt-get purge --auto-remove redis-server -y

# Remove Redis configuration and data directories (optional)
echo "Removing Redis configuration and data files..."
sudo rm -rf /etc/redis /var/lib/redis

# Verify Redis is uninstalled
if ! command -v redis-server &> /dev/null
then
    echo "Redis successfully uninstalled."
else
    echo "Redis is still installed."
fi
