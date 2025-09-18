#!/bin/env bash

# with environment variables.

set -e

SCRIPT_DIR=$(dirname "$0")

export RM_BASE=$(realpath "$SCRIPT_DIR/..")

SERVICE_ETC="/etc/systemd/system/rm-queue.service"
SERVICE_LOCAL="$RM_BASE"/deploy/rm-queue.service

echo "Copying $SERVICE_LOCAL to $SERVICE_LOCAL and substituting environment variables"

sudo cp "$SERVICE_ETC" "$SERVICE_ETC".bak || echo "Backup of $SERVICE_ETC failed"

# Replace environment variables in the service file
tempfile=$(mktemp)
envsubst < "$SERVICE_LOCAL" > "$tempfile"

sudo cp "$tempfile" "$SERVICE_ETC"

sudo systemctl daemon-reload

echo "Contents of $SERVICE_ETC:"
echo "------------------------"
sudo cat "$SERVICE_ETC"
echo "------------------------"
echo "Run 'sudo systemctl restart rm-queue' and/or 'sudo systemctl enable rm-queue'"
echo "Run 'sudo journalctl -u rm-queue -f' to view logs"