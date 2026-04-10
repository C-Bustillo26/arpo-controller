#!/bin/bash
set -e

echo "Updating package list..."
sudo apt update

echo "Installing Python tools..."
sudo apt install -y python3-pip

echo "Installing Python packages..."
pip3 install --break-system-packages -r requirements.txt

echo "Setup complete."
