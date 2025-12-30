# iDotMatrix Home Assistant Integration

A custom component for [Home Assistant](https://www.home-assistant.io/) to control **iDotMatrix** Bluetooth displays.

## Features
- **Control:** Switch clock faces, animations, and text modes.
- **Text:** Send text messages to the display.
- **Sync:** Synchronize device time with Home Assistant.
- **Images:** Upload images (Coming Soon).
- **Weather:** Sync weather data (Coming Soon).

## Installation

### HACS (Recommended)
1.  Open HACS in Home Assistant.
2.  Go to "Integrations" > "Explore & Download Repositories".
3.  Search for `iDotMatrix`.
4.  Click "Download".
5.  Restart Home Assistant.

### Manual
1.  Download this repository.
2.  Copy the `custom_components/idotmatrix` folder to your HA `config/custom_components/` directory.
3.  Restart Home Assistant.

## Configuration
1.  Go to **Settings** > **Devices & Services**.
2.  Click **Add Integration**.
3.  Search for **iDotMatrix**.
4.  Enter your device's MAC address (or wait for auto-discovery if supported).

## Usage
- **Services:** `text.set_value` to send text.
- **Select:** Change clock styles via the Select entity.

## Credits
Based on the `python3-idotmatrix-client` library.
