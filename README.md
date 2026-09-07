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
- Running any portal (even a simulation) against real victims outside your own lab
- Capturing real credentials — this build uses lab-fake creds and RSA-redacts to sha256 prefixes
- Any activity that violates applicable laws or regulations — the Python engine emits no radio
- Commercial use without proper licensing

### Regulatory Framework
- **Federal Communications Act (47 U.S.C. § 333)**: Willful interference with authorized radio communications is prohibited.
- **47 CFR Part 15**: Unauthorized intentional radiators are regulated; this repo is byte-level simulation only.
- **CFAA (18 U.S.C. § 1030) / ECPA / State computer-crime laws**: Impersonating a hotspot and harvesting credentials from networks you don't own is a serious federal and state crime.
- Deploying a real evil-twin portal requires written scope over enabled networks with clear victim notice — even then, use sanctioned phishing-simulation tools, not this codebase.

## Live Lab Test Plan

Offline (this repo, no radio):
1. Gated simulation:
   `python3 firmware/evil_portal.py --simulate --lab-ssid lab-test-net
   --i-understand-this-is-an-offline-lab-simulation-with-no-radio-emission --json reports/w8.json`
   — beacon + probe + auth frames as bytes, portal GET/POST + DNS wildcard, exit 0.
2. Negative gates: `--simulate` without the flag -> exit 2; non-`lab-*` SSID -> exit 2.
3. `python3 -m unittest discover -s tests` — byte-exact beacon/auth, redaction tests (exit 0).

Authorized lab (simulation of YOUR OWN AP only):
4. Clone your own lab AP's SSID in a shielded enclosure; verify captured posts carry only fake
   credentials and the JSON report is sha256-redacted.
5. `green = permitted`: offline beacon/portal byte simulation; nothing transmitted.

## Metrics

- Evil-twin beacon (byte-exact, frame_core): clone lab SSID, interval 100, FCS verified
- Association simulation: probe-request + open auth (AUTH_ALG_OPEN) all FCS-verified as bytes
- Captive portal: GET / -> login form, POST /login -> capture + success, wildcard DNS ->
  PORTAL_IP (192.0.2.4 TEST-NET only, never a real address)
- Credential handling: accepted only in the gated lab path; JSON stores sha256 prefix (16 hex),
  never plaintext; `credential-logs/` gitignored
- Safety gate: simulation requires confirmation flag AND `lab-*` SSID; exit 2 otherwise
- Offline: no radio; no wall-clock-dependent frame data (codes are the only realism)

- Test suite: `python3 -m unittest discover -s tests`
- Reports: `reports/` (gitignored)
- Associated firmware: `firmware/w8_evil_portal/w8_evil_portal.ino` (ESP32-C6)

## License

MIT
