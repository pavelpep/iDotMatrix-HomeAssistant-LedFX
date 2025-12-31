#!/bin/bash
# Script to run Home Assistant Core locally for testing custom components with Bluetooth support on macOS

# 1. Create a new venv for Home Assistant (separate from the project venv)
echo "Creating Home Assistant venv using Python 3.12..."
rm -rf ha_venv
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12 -m venv ha_venv

# 2. Activate and install Home Assistant
source ha_venv/bin/activate
echo "Installing Home Assistant (this may take a while)..."
# Fix known macOS dependency issues:
# The latest pycares (v5+) breaks aiodns with "TypeError: Channel.getaddrinfo".
# We need to pin pycares to <5.0.0 to make aiodns work.
pip install "pycares<5.0.0"
pip install homeassistant

# 3. Create a config directory
mkdir -p config
mkdir -p config/custom_components

# 4. Link the custom component
echo "Linking iDotMatrix integration..."
rm -rf config/custom_components/idotmatrix
ln -s "$(pwd)/custom_components/idotmatrix" "$(pwd)/config/custom_components/idotmatrix"

# 4b. Configure port 8128
echo "Configuring custom port 8128..."
echo "default_config:" > config/configuration.yaml
echo "http:" >> config/configuration.yaml
echo "  server_port: 8128" >> config/configuration.yaml

# 5. Run Home Assistant
echo "Starting Home Assistant..."
echo "Access it at http://localhost:8128"
hass -c config
