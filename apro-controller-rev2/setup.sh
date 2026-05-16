#!/bin/bash
set -e

echo "Updating package list..."
sudo apt update

echo "Installing system packages..."
sudo apt install -y python3-pip python3-smbus i2c-tools git

echo "Installing Python packages..."
pip3 install --break-system-packages -r requirements.txt

echo "Setup complete."
