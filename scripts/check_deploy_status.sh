#!/bin/bash

# Function to check if a service is running
check_service_status() {
    service_name=$1
    display_name=$2
    
    if systemctl is-active --quiet $service_name; then
        echo "$display_name is running."
    else
        echo "$display_name is NOT running!"
        echo "Error log:"
        journalctl -u $service_name --since "1 minutes ago"
        echo ""
    fi
}

# Check the status of Nginx, Gunicorn (todo-unicorn), and PostgreSQL
check_services() {
    echo "Checking service status..."

    check_service_status nginx "Nginx"
    check_service_status rm-server "rm-server (Gunicorn)"
    check_service_status postgresql "PostgreSQL"
    
    echo "Service check completed."
}

# Run the check
check_services
