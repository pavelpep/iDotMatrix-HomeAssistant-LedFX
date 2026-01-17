# iDotMatrix Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/adriantukendorf/iDotMatrix-HomeAssistant)](https://github.com/adriantukendorf/iDotMatrix-HomeAssistant/releases)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-yellow.svg)](https://buymeacoffee.com/tukie)

A fully featured, modern Home Assistant integration for **iDotMatrix** pixel art displays. 

Connects directly to your device via Bluetooth (native or proxy) without any cloud dependencies. Unlock the full potential of your display with advanced animations, typography controls, "Party Mode" features, and **LedFX integration for audio-reactive visualizations**!

---

## ✨ Features

- **🚀 Instant Bluetooth Connectivity**: Supports native adapters and ESPHome Bluetooth Proxies for rock-solid connections.
- **🎵 LedFX Gateway** (NEW!):
    - **Real-time audio visualizations** from LedFX to your iDotMatrix display.
    - Built-in UDP server compatible with WLED protocol.
    - Intelligent frame skipping and rate limiting for optimal performance.
    - 20-30 FPS with automatic optimization.
- **📝 Advanced Text Engine**: 
    - Full control over Font, Color, Speed, and Animation Mode.
    - **Pixel Perfect Fonts**: Comes with built-in bitmap fonts (e.g., VT323, Press Start 2P) for crisp rendering.
    - **Typography Controls**: Adjust Letter Spacing (horizontal/vertical), Blur/Sharpness, and Font Size.
- **🎉 Fun Text (Party Mode)**: 
    - Animates messages word-by-word with random bright colors.
    - Adjustable delay for perfect timing.
- **📏 Autosize Perfect Fit**: 
    - Automatically scales text to perfectly fit the screen bounds, centering it for a pro look.
- **🕰️ Clock Control**: 
    - Syncs time automatically.
    - Customizable 12h/24h formats, date display, and colors.
- **🎨 Drawing & Images**:
    - Upload images (coming soon) or text-as-images (Multiline support).
    - Control panel brightness and screen dimensions (16x16 / 32x32 / 64x64).
- **🔋 Device Control**:
    - Turn On/Off, set Brightness, colour.

---

## 🎵 LedFX Gateway Setup

Transform your iDotMatrix into an audio-reactive LED visualizer!

### Prerequisites

1. **LedFX** installed and running ([ledfx.app](https://ledfx.app/))
2. **iDotMatrix display** connected via this integration

### Setup Steps

1. **Configure LedFX**:
   - Open LedFX and go to **Devices**
   - Add a new **WLED** device
   - Set the IP to your Home Assistant server (e.g., `192.168.1.100`)
   - Set the port to `21324` (or your configured port)
   - Configure as a **32x32 matrix** (1024 pixels)

2. **Enable the Gateway in Home Assistant**:
   - Go to your iDotMatrix device in Home Assistant
   - Find the **"LedFx Gateway"** switch and turn it **ON**
   - Optionally adjust **LedFx UDP Port** (default: 21324)
   - Optionally adjust **LedFx Max FPS** (default: 30)

3. **Start Visualizing!**:
   - Play music and apply effects in LedFX
   - Watch real-time audio visualizations on your iDotMatrix!

### Architecture

```
┌─────────┐    UDP     ┌─────────────────────┐    BLE      ┌─────────────┐
│  LedFX  │ ───────→   │   Home Assistant    │ ──────────→ │ iDotMatrix  │
│         │  Port      │   (LedFx Gateway)   │ Optimized   │   Display   │
│         │  21324     │                     │ PNG Data    │   32x32     │
└─────────┘            │ • Frame Compression │             └─────────────┘
                       │ • Rate Limiting     │
                       │ • Skip Duplicates   │
                       └─────────────────────┘
```

### Performance Tips

- **Position matters**: Keep display close to Bluetooth adapter/proxy
- **Dark themes**: Use darker color schemes in LedFX for higher FPS
- **Adjust Max FPS**: Lower values reduce Bluetooth load
- **Monitor FPS**: Check the "LedFx Gateway FPS" sensor for performance

---

## 🛠️ Installation

### Option 1: HACS (Recommended)
1. Open HACS in Home Assistant.
2. Go to **Integrations** > **Triple Dots** > **Custom Repositories**.
3. Add `https://github.com/adriantukendorf/iDotMatrix-HomeAssistant` as an **Integration**.
4. Click **Download**.
5. Restart Home Assistant.

### Option 2: Manual
1. Download the `custom_components/idotmatrix` folder from this repository.
2. Copy it to your Home Assistant `config/custom_components/` directory.
3. Restart Home Assistant.

---

## ⚙️ Configuration

1. Go to **Settings** > **Devices & Services**.
2. Click **Add Integration** and search for **iDotMatrix**.
3. The integration will automatically discover nearby devices. Select your device.
    - *Note: Ensure your device is powered on and not connected to the phone app.*

---

## 📖 Usage Guide

### 📝 Text Control
Control the scrolling text on your device using the `Display Text` entity.
- **Entity**: `text.idotmatrix_display_text`
- **Actions**: Type any text to update the display immediately.
- **Settings**: Use the configuration entities (sliders/selects) to adjust:
    - **Font**: Choose from installed pixel-perfect fonts.
    - **Speed**: Scroll speed (1-100).
    - **Color**: Full RGB control via `light.idotmatrix_panel_colour`.
    - **Spacing**: Tweak kerning with "Text Spacing".

### 🎉 Fun Text (Party Mode)
Want to spice things up? Use the Fun Text entity!
- **Entity**: `text.idotmatrix_fun_text`
- **How it works**:
    1. Enter a phrase like "HAPPY NEW YEAR".
    2. The display will show one word at a time.
    3. Each word gets a **random bright color** from a curated palette.
- **Control**: Adjust the speed of the animation with the **Fun Text Delay** slider (`number.idotmatrix_fun_text_delay`).

### 📏 Autosize (Perfect Fit)
Stop guessing font sizes. Let the integration do the math.
- **Entity**: `switch.idotmatrix_text_perfect_fit_autosize`
- **How it works**:
    - **ON**: The integration iteratively resizes your text (shrinking from max size) until it fits perfectly within the screen capabilities 
    - **OFF**: Standard scrolling or manual font size.

### 🕰️ Clock & Time
- **Sync Time**: Press `button.idotmatrix_sync_time` to instantly sync the device clock to Home Assistant's time.
- **Formats**: Toggle `select.idotmatrix_clock_format` (12h/24h) and `switch.idotmatrix_clock_show_date`.

### 📶 Bluetooth Proxy
This integration fully supports **ESPHome Bluetooth Proxies**.
- If your Home Assistant server is far from the device, use a cheap ESP32 with ESPHome to extend range.
- The integration will automatically find and use the proxy with the best signal.

---

## 📦 Entities Reference

### Switches
| Entity | Description |
|--------|-------------|
| `switch.idotmatrix_ledfx_gateway` | Enable/disable LedFX audio visualization gateway |
| `switch.idotmatrix_text_perfect_fit_autosize` | Auto-scale text to fit screen |
| `switch.idotmatrix_multiline_text` | Enable multiline text mode |
| `switch.idotmatrix_clock_show_date` | Show date on clock |
| `switch.idotmatrix_proportional_spacing` | Enable proportional font spacing |

### Numbers
| Entity | Description |
|--------|-------------|
| `number.idotmatrix_ledfx_udp_port` | UDP port for LedFX (default: 21324) |
| `number.idotmatrix_ledfx_max_fps` | Maximum FPS for LedFX gateway (5-60) |
| `number.idotmatrix_text_speed` | Text scroll speed (1-100) |
| `number.idotmatrix_text_font_size` | Font size (6-64) |
| `number.idotmatrix_text_horizontal_spacing` | Horizontal letter spacing |
| `number.idotmatrix_text_vertical_spacing` | Vertical line spacing |
| `number.idotmatrix_text_sharpness_blur` | Text blur/sharpness (0-5) |
| `number.idotmatrix_fun_text_delay` | Fun text word delay (0.2-5.0 sec) |

### Sensors
| Entity | Description |
|--------|-------------|
| `sensor.idotmatrix_ledfx_gateway_fps` | Current FPS of LedFX gateway |

### Selects
| Entity | Description |
|--------|-------------|
| `select.idotmatrix_text_font` | Font selection |
| `select.idotmatrix_text_animation` | Text animation mode |
| `select.idotmatrix_text_color_mode` | Color mode (solid, rainbow, etc.) |
| `select.idotmatrix_clock_format` | Clock format (12h/24h) |
| `select.idotmatrix_clock_style` | Clock style |
| `select.idotmatrix_screen_size` | Screen size (16x16, 32x32, 64x64) |

### Other
| Entity | Description |
|--------|-------------|
| `text.idotmatrix_display_text` | Main display text |
| `text.idotmatrix_fun_text` | Fun/party text mode |
| `light.idotmatrix_panel_colour` | Panel color control |
| `button.idotmatrix_sync_time` | Sync clock to HA time |

---

## 🔧 Troubleshooting

**"Device unavailable" / "No backend found"**
- Ensure the device is **disconnected** from the mobile app. It can only talk to one controller at a time.
- If using a local adapter on macOS/Linux, ensure BlueZ is up to date.
- Restart the iDotMatrix device (unplug/replug).

**LedFX not showing on display**
- Verify the LedFX Gateway switch is **ON**
- Check LedFX is configured with the correct IP and port
- Ensure LedFX device is set to 32x32 (1024 pixels)
- Check the "LedFx Gateway FPS" sensor - if 0, data isn't being received
- Make sure your firewall allows UDP traffic on port 21324

**Low FPS in LedFX mode**
- **Dark scenes**: Should achieve 25-30 FPS
- **Colorful scenes**: Expect 15-25 FPS
- **Below 10 FPS**: Check BLE connection strength, move closer to adapter/proxy
- Try lowering Max FPS setting to reduce Bluetooth congestion

**Blocking Calls / Slow Startup**
- This integration uses non-blocking async calls for all operations to ensure your Home Assistant remains snappy.

---

## 🙏 Credits

- Original integration by [Adrian Tukendorf](https://github.com/adriantukendorf)
- LedFX Gateway based on [idotmatrixXLedFx](https://github.com/suchyindustries/idotmatrixXLedFx) by suchyindustries
- iDotMatrix client based on [python3-idotmatrix-client](https://github.com/derkalle4/python3-idotmatrix-client)

---
