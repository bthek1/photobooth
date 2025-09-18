#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "Uninstalling PostgreSQL..."

# Stop PostgreSQL service
sudo systemctl stop postgresql

# Disable PostgreSQL service
sudo systemctl disable postgresql

# Remove PostgreSQL packages
sudo apt-get --purge remove -y postgresql\* postgresql-contrib

# Remove PostgreSQL data and configuration directories
sudo rm -rf /etc/postgresql
sudo rm -rf /var/lib/postgresql
sudo rm -rf /var/log/postgresql

# Optionally remove the PostgreSQL user
if id "postgres" &>/dev/null; then
    sudo userdel -r postgres
fi

# Clean up package manager
sudo apt-get autoremove -y
sudo apt-get autoclean

echo "PostgreSQL uninstalled successfully."
