#!/usr/bin/env python3
"""Byte-exact unit tests for w8-evil-portal."""

import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from firmware import evil_portal as ep
from firmware import frame_core as fc

FLAG = ep.SAFETY_FLAG


class BeaconTest(unittest.TestCase):
    def test_evil_beacon_parses_back(self):
        data = ep.build_evil_beacon("lab-test-net", seq_num=5)
        self.assertTrue(fc.verify_fcs(data))
        p, _ = fc.parse_beacon(data[:-4])
        self.assertEqual(p["ssid"], "lab-test-net")
        self.assertEqual(p["seq_num"], 5)

    def test_association_all_fcs_ok(self):
        frames = ep.simulate_association("lab-test-net")
        self.assertEqual([f["kind"] for f in frames],
                         ["beacon", "probe-request", "auth"])
        for f in frames:
            self.assertTrue(fc.verify_fcs(f["data"]))


class PortalTest(unittest.TestCase):
    def test_get_serves_login(self):
        p = ep.CaptivePortal("lab-test-net")
        code, body = p.get("/")
        self.assertEqual(code, 200)
        self.assertIn("/login", body)

    def test_post_login_captures_redacted(self):
        p = ep.CaptivePortal("lab-test-net")
        code, body = p.post_login({"ssid": "lab-test-net", "password": "s3cret!"})
        self.assertEqual(code, 200)
        self.assertEqual(len(p.captures), 1)
        rec = p.captures[0]
        self.assertEqual(rec["password_len"], 7)
        self.assertNotIn("s3cret!", json.dumps(p.captures))
        self.assertEqual(rec["password_redacted"], ep.redact("s3cret!"))

    def test_dns_wildcard_testnet(self):
        p = ep.CaptivePortal()
        self.assertEqual(p.dns_wildcard("captive.example"), "192.0.2.4")


class RedactTest(unittest.TestCase):
    def test_deterministic_and_prefix(self):
        a = ep.redact("hunter2")
        b = ep.redact("hunter2")
        self.assertEqual(a, b)
        self.assertEqual(len(a), 16)
        self.assertNotEqual(a, "hunter2")


class GateTest(unittest.TestCase):
    def test_sim_no_flag_exit2(self):
        with self.assertRaises(SystemExit) as cm:
            ep.main(["--simulate", "--lab-ssid", "lab-test-net"])
        self.assertEqual(cm.exception.code, 2)

    def test_sim_bad_ssid_exit2(self):
        with self.assertRaises(SystemExit) as cm:
            ep.main(["--simulate", FLAG, "--lab-ssid", "corp-wifi"])
        self.assertEqual(cm.exception.code, 2)


class CLITest(unittest.TestCase):
    def test_demo_exit_zero(self):
        self.assertEqual(ep.run_demo(), 0)

    def test_json_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "o.json")
            rc = ep.main([FLAG, "--lab-ssid", "lab-test-net", "--simulate", "--json", out])
            self.assertEqual(rc, 0)
            data = json.load(open(out))
            self.assertFalse(data["radio_emitted"])
            self.assertEqual(len(data["portal"]["captures"]), 1)
            self.assertEqual(len(data["frames"]), 3)


if __name__ == "__main__":
    unittest.main()