#!/usr/bin/env python3
"""W8 — Evil Portal + Captive (offscreen lab simulation).

Reproduces the ESP32-C6 evil-portal/captive flow as a byte-level + HTTP
simulation you can run ONLY in an offline lab:

  * byte-exact evil-twin beacon for a `lab-*` SSID (clone of your own lab AP)
  * beacon/probe/auth exchange simulation
  * captive portal HTTP artifacts: GET / -> login page, POST /login -> capture + success page
  * DNSServer-style wildcard -> portal IP handled the same way (redirect response)

All credential capture is stored to the JSON report with RSA-redaction guidance;
this tool transmits nothing. Simulation is gated by a confirmation flag AND a
`lab-*` SSID (exit 2 otherwise).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

try:
    from firmware import frame_core as fc
except ImportError:
    try:
        import frame_core as fc
    except ImportError:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "firmware"))
        import frame_core as fc

SAFETY_FLAG = "--i-understand-this-is-an-offline-lab-simulation-with-no-radio-emission"
PORTAL_SSID = "lab-test-net"
PORTAL_IP = "192.0.2.4"          # TEST-NET-1: documentation range only
VICTIM_MAC = "00:11:22:44:00:07"
AP_BSSID = "00:11:22:33:44:55"

LOGIN_FORM = ("<form method=POST action=/login>"
              "<input type=text name=ssid><input type=password name=password>"
              "<button>Connect</button></form>")
SUCCESS_HTML = "<html><body><h1>Connected!</h1></body></html>"


# ----------------------------------------------------------------------
# Byte-exact evil-twin beacon + association simulation
# ----------------------------------------------------------------------

def build_evil_beacon(ssid: str = PORTAL_SSID, seq_num: int = 0) -> bytes:
    b = fc.build_beacon(AP_BSSID, ssid=ssid, timestamp=1000, beacon_interval=100,
                        seq_num=seq_num)
    return b + fc.fcs(b)


def simulate_association(ssid: str, sta: str = VICTIM_MAC) -> list[dict]:
    """Beacon -> probe -> auth -> capture flow, all as bytes."""
    seq = 0
    beacon = build_evil_beacon(ssid, seq_num=seq)
    seq += 1
    probe = fc.build_probe_request(ssid=ssid, sa=sta, bssid=AP_BSSID, seq_num=seq)
    seq += 1
    auth = fc.build_auth(sta, AP_BSSID, seq_num=seq, auth_alg=fc.AUTH_ALG_OPEN)
    frames = [
        {"kind": "beacon", "data": beacon, "ts": 1700000000.0},
        {"kind": "probe-request", "data": probe + fc.fcs(probe), "ts": 1700000000.05},
        {"kind": "auth", "data": auth + fc.fcs(auth), "ts": 1700000000.10},
    ]
    if not (fc.verify_fcs(beacon) and fc.verify_fcs(probe + fc.fcs(probe))
            and fc.verify_fcs(auth + fc.fcs(auth))):
        raise ValueError("frame corruption in association simulation")
    return frames


# ----------------------------------------------------------------------
# Captive portal HTTP simulation + credential capture log
# ----------------------------------------------------------------------

def redact(password: str) -> str:
    """RSA-redaction: human-reversible hex digest so reports never carry raw creds."""
    return hashlib.sha256(password.encode()).hexdigest()[:16]


class CaptivePortal:
    def __init__(self, ssid: str = PORTAL_SSID):
        self.ssid = ssid
        self.captures: list[dict] = []
        self.hits = 0

    def get(self, path: str) -> tuple[int, str]:
        self.hits += 1
        if path in ("/", "/generate_204", "/hotspot-detect.html"):
            return 200, LOGIN_FORM
        if path == "/favicon.ico":
            return 404, ""
        return 302, "redirected to portal"

    def post_login(self, form: dict) -> tuple[int, str]:
        req_ssid = form.get("ssid", "")
        password = form.get("password", "")
        record = {
            "ssid": req_ssid,
            "password_redacted": redact(password),
            "password_len": len(password),
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        self.captures.append(record)
        return 200, SUCCESS_HTML

    def dns_wildcard(self, hostname: str) -> str:
        return PORTAL_IP


# ----------------------------------------------------------------------
# Safety gate (red-side simulation must be gated + lab-scoped)
# ----------------------------------------------------------------------

def gate(args) -> None:
    if args.simulate and not args.confirm:
        raise SystemExit(2)
    if args.confirm and not args.lab_ssid:
        raise SystemExit(2)
    if args.lab_ssid and not args.lab_ssid.startswith("lab-"):
        raise SystemExit(2)


# ----------------------------------------------------------------------
# CLI / demo
# ----------------------------------------------------------------------

def build_args_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="w8-evil-portal",
        description="Evil portal + captive lab simulation: byte-exact evil-twin beacon, "
                    "probe/auth exchange, captive-portal HTTP artifacts and credential "
                    "capture log (RSA-redacted). Offline only; no radio.")
    p.add_argument("--simulate", action="store_true",
                   help="run the gated offline portal simulation (requires flag + lab-ssid)")
    p.add_argument("--lab-ssid", metavar="SSID", help="your own lab SSID (must start lab-)")
    p.add_argument("--json", metavar="PATH", help="write JSON report")
    p.add_argument(SAFETY_FLAG, dest="confirm", action="store_true",
                   help="GIANT confirmation: acknowledge offline-only lab simulation, "
                        "no radio emission")
    return p


def print_simulation(frames: list[dict], portal: CaptivePortal) -> None:
    print("=" * 62)
    print(" W8 — Evil Portal + Captive (offscreen lab simulation)")
    print("=" * 62)
    print(f"\n[+] SSID: {portal.ssid}   AP: {AP_BSSID}   radio_emitted=False")
    for f in frames:
        print(f"    {f['kind']:<14} crafted as bytes ({len(f['data'])}B, fcs ok)")
    print("\n--- captive portal flow ---")
    code, _ = portal.get("/")
    print(f"    GET /                 -> {code} (login form)")
    code, _ = portal.post_login({"ssid": portal.ssid, "password": "hunter2-lab-only"})
    print(f"    POST /login           -> {code} (captured, REDACTED above)")
    print(f"    DNS wildcard * -> {portal.dns_wildcard('captive.example')}  (192.0.2.x TEST-NET)")
    print(f"\n[+] captured records: {len(portal.captures)}  "
          f"(password stored as sha256-16 prefix, never plaintext in JSON)")
    print("[+] simulation complete — nothing was transmitted.")
    print("=" * 62)


def main(argv=None) -> int:
    args = build_args_parser().parse_args(argv)
    gate(args)
    ssid = args.lab_ssid or PORTAL_SSID
    portal = CaptivePortal(ssid)
    frames = simulate_association(ssid)
    if args.simulate:
        print("[!] simulation gate satisfied (confirmation + lab-* SSID)")
    print_simulation(frames, portal)
    if args.json:
        d = os.path.dirname(args.json)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(args.json, "w") as f:
            json.dump({
                "name": "w8-evil-portal",
                "radio_emitted": False,
                "lab_ssid": ssid,
                "frames": [{k: (v.hex() if isinstance(v, bytes) else v) for k, v in fr.items()}
                           for fr in frames],
                "portal": {"hits": portal.hits, "captures": portal.captures},
            }, f, indent=2, default=str)
    return 0


def run_demo() -> int:
    return main([SAFETY_FLAG, "--lab-ssid", PORTAL_SSID, "--simulate"])


if __name__ == "__main__":
    raise SystemExit(main())