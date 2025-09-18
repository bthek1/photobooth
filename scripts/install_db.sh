#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo ".env file not found!"
    exit 1
fi

# Function to install PostgreSQL if it's not already installed
install_postgres() {
    if ! dpkg -l | grep -q postgresql; then
        echo "Installing PostgreSQL..."
        sudo apt update
        sudo apt install -y postgresql postgresql-contrib
    else
        echo "PostgreSQL is already installed."
    fi
}


# Function to start PostgreSQL service
start_postgres() {
    echo "Starting PostgreSQL service..."
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
}


# Main script execution
install_postgres
start_postgres


echo "PostgreSQL setup completed."
