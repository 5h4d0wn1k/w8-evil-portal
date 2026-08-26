# W8 — Evil Portal + Captive

Create evil twin AP with realistic captive portal for credential capture.

## Overview

This project implements an evil twin attack with a professional-looking captive portal that:
- Clones any WiFi SSID
- Presents a realistic WiFi login page
- Captures credentials when users enter them
- Supports multiple portal templates

**WARNING: Educational use only. Test on your own lab network.**

## Hardware

| Component | Connection | Role |
|-----------|------------|------|
| ESP32-C6 | Main board | Evil twin AP |

## Serial Commands

```
start <SSID> - Start evil portal with given SSID
stop         - Stop evil portal
creds        - Show captured credentials
help         - Show commands
```

## Captured Output

```
*** CREDENTIAL CAPTURED ***
SSID: MyHomeWiFi
Password: mysecretpassword
**************************
```

## Build & Flash

```bash
arduino-cli compile --fqbn esp32:esp32:esp32c6 w8_evil_portal
arduino-cli upload --fqbn esp32:esp32:esp32c6 --port /dev/ttyACM0 w8_evil_portal
```

## References

- IEEE 802.11 Management Frames
- Captive Portal Implementation

## License

MIT
