#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Load environment variables from .env file if available
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo ".env file not found! Skipping environment setup."
fi

# Function to install PostgreSQL if it's not installed
install_postgres() {
    if ! brew list | grep -q postgresql; then
        echo "Installing PostgreSQL..."
        brew update
        brew install postgresql
    else
        echo "PostgreSQL is already installed."
    fi
}

# Function to start PostgreSQL service
start_postgres() {
    echo "Starting PostgreSQL service..."
    brew services start postgresql
}

# Function to create a PostgreSQL user
create_postgres_user() {
    echo "Checking if 'postgres' user exists..."
    if ! psql -U "$(whoami)" -d postgres -c "\du" | grep -qw postgres; then
        echo "Creating 'postgres' user..."
        psql -U "$(whoami)" -d postgres -c "CREATE ROLE postgres WITH SUPERUSER LOGIN PASSWORD 'yourpassword';"
    else
        echo "'postgres' user already exists."
    fi
}

# Main script execution
install_postgres
start_postgres

# Wait for PostgreSQL to start (avoid timing issues)
sleep 5

# Ensure a database exists before creating a user
if ! psql -U "$(whoami)" -lqt | cut -d \| -f 1 | grep -qw postgres; then
    echo "Creating 'postgres' database..."
    createdb -U "$(whoami)" postgres
fi

# Create the 'postgres' user
create_postgres_user

echo "✅ PostgreSQL setup completed successfully!"
