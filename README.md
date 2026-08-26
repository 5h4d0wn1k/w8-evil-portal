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

## Legal Disclaimer

**IMPORTANT: Read before use.**

This project is provided for **educational and authorized security testing purposes only**. 

### Authorization Requirements
- You MUST have explicit written permission from the network owner before using this tool
- Unauthorized interception of network communications is illegal under federal and state laws
- This tool should ONLY be used on networks you own or have written authorization to test

### Legal Framework
- **Computer Fraud and Abuse Act (CFAA)**: Unauthorized access to computer systems is a federal crime
- **Wiretap Act (18 U.S.C. § 2511)**: Interception of electronic communications without consent is illegal
- **State Laws**: Many states have additional computer crime and wiretapping statutes
- **GDPR/CCPA**: Data collection may be subject to privacy regulations

### Acceptable Use
- Testing security of your own networks
- Authorized penetration testing with written scope
- Academic research in controlled lab environments
- Security education and training

### Prohibited Use
- Intercepting communications on networks you do not own
- Attacking infrastructure without authorization
- Any activity that violates applicable laws or regulations
- Commercial use without proper licensing

### No Warranty
This software is provided "AS IS" without warranty of any kind. The author is not responsible for any misuse or damage caused by this software.

### Responsible Disclosure
If you discover vulnerabilities using this tool, follow responsible disclosure practices:
1. Report to the vendor/owner privately
2. Allow reasonable time for remediation
3. Do not exploit beyond proof of concept
