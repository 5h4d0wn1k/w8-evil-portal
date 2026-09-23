> **⚠️ EDUCATIONAL USE ONLY — AUTHORIZED TESTING ONLY.**
> This project exists for education, research, and **defense of systems you own
> or hold explicit written authorization to assess**. Unauthorized use is
> prohibited and may be illegal. Read [ETHICS.md](ETHICS.md) and
> [SCOPE.md](SCOPE.md) before use. Use at your own risk; **AS IS**, no warranty.

# W8 — Evil Portal + Captive-Portal Simulator (Wi-Fi Security Lab)

Offline, byte-level simulation of an evil-twin AP and captive portal for wireless security labs — crafted beacon/probe/auth frames, a realistic login flow, and RSA-redacted credential-capture records. No radio is ever emitted.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/5h4d0wn1k/w8-evil-portal.svg)](https://github.com/5h4d0wn1k/w8-evil-portal)
[![Last commit](https://img.shields.io/github/last-commit/5h4d0wn1k/w8-evil-portal.svg)](https://github.com/5h4d0wn1k/w8-evil-portal)
[![Issues](https://img.shields.io/github/issues/5h4d0wn1k/w8-evil-portal.svg)](https://github.com/5h4d0wn1k/w8-evil-portal)

## Why

Evil-twin attacks are a defining threat in Wi-Fi security education — and a category where behavior is best studied in bytes, not in the air. W8 simulates the entire flow offscreen: byte-exact 802.11 beacon frames for a cloned lab SSID, probe/authentication exchanges, a captive-portal HTTP login form, wildcard-DNS fallback, and credential-capture records that store only a sha256 prefix. Learning the mechanics of phishing-adjacent wireless attacks in a simulator teaches defenders what to look for without risking real users or radio spectrum.

## Features

- **Byte-exact evil-twin beacon** (`frame_core`) — clone a `lab-*` SSID, interval 100, FCS verified
- **Association simulation** — probe request + open-auth frames as verified bytes
- **Captive-portal flow** — `GET /` serves a login form, `POST /login` captures; wildcard DNS resolves to `192.0.2.4` TEST-NET only
- **Redacted credential capture** — JSON stores a 16-hex sha256 prefix, never plaintext; `credential-logs/` gitignored
- **Hard safety gate** — requires `--i-understand-this-is-an-offline-lab-simulation-with-no-radio-emission` and a `lab-` SSID; anything else exits 2
- **ESP32-C6 reference firmware** — `firmware/w8_evil_portal/` for authorized lab builds

## Quickstart

```bash
git clone https://github.com/5h4d0wn1k/w8-evil-portal.git && cd w8-evil-portal

# Offline gated simulation of your own lab AP (no radio)
python3 firmware/evil_portal.py --simulate --lab-ssid lab-test-net \
    --i-understand-this-is-an-offline-lab-simulation-with-no-radio-emission \
    --json reports/w8.json

# Unit tests (byte-exact frames + redaction)
python3 -m unittest discover -s tests
```

## Project structure

- `firmware/evil_portal.py` — portal simulator CLI (`--simulate`), `firmware/frame_core.py` — frame builder
- `firmware/w8_evil_portal/` — ESP32-C6 reference firmware (Arduino)
- `tests/` — beacon/auth byte-exactness and redaction unit tests

## Documentation

- [ETHICS.md](ETHICS.md) — educational purpose and authorized use only
- [SCOPE.md](SCOPE.md) — authorized-testing scope checklist
- [SECURITY.md](SECURITY.md) — vulnerability reporting
- [CONTRIBUTING.md](CONTRIBUTING.md) — safe contribution guidelines

## Contributing

Improvements to frame fidelity, portal templates and redaction tests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md); the simulator must stay offline and emission-free.

## License

MIT — see [LICENSE](LICENSE). Provided **AS IS**, without warranty, for education and authorized wireless-security lab use only.