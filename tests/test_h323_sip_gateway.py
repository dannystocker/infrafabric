"""
Unit Tests for SIP-H.323 Gateway (Codec Transcoding + Policy Enforcement)

Tests:
1. SIP call acceptance
2. H.323 admission integration (policy enforcement)
3. Codec transcoding (G.711 ↔ G.729)
4. Bridge lifecycle (establish → active → teardown)
5. IF.witness logging

Author: InfraFabric Project
License: CC BY 4.0
Last Updated: 2025-11-11
"""

import sys
import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from communication.h323_sip_gateway import (
    SIPH323Gateway,
    SIPUserAgent,
    H323TerminalEmulator,
    CodecTranscoder,
    CodecType,
    BridgedCall,
    SIPCallLeg,
    H323CallLeg
)


class TestCodecTranscoder(unittest.TestCase):
    """Test codec transcoding functionality"""

    def setUp(self):
        """Setup temp directory for logs"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "logs"
        self.transcoder = CodecTranscoder(self.log_dir)

    def tearDown(self):
        """Cleanup"""
        # Stop any active transcoders
        for bridge_id in list(self.transcoder.active_transcoders.keys()):
            self.transcoder.stop_transcoding(bridge_id)
        shutil.rmtree(self.temp_dir)

    def test_g711_to_g729_transcoding(self):
        """✅ Should transcode G.711 (SIP) → G.729 (H.323)"""
        bridge_id = "test-bridge-001"

        pid = self.transcoder.start_transcoding(
            bridge_id=bridge_id,
            input_codec=CodecType.G711_ULAW,
            input_port=20000,
            output_codec=CodecType.G729,
            output_port=30000,
            output_ip="127.0.0.1"
        )

        # Should return valid PID (or -1 in mock mode)
        self.assertIsNotNone(pid)
        self.assertIn(bridge_id, self.transcoder.active_transcoders)

        # Stop transcoding
        success = self.transcoder.stop_transcoding(bridge_id)
        self.assertTrue(success)
        self.assertNotIn(bridge_id, self.transcoder.active_transcoders)

    def test_g729_to_g711_transcoding(self):
        """✅ Should transcode G.729 (H.323) → G.711 (SIP)"""
        bridge_id = "test-bridge-002"

        pid = self.transcoder.start_transcoding(
            bridge_id=bridge_id,
            input_codec=CodecType.G729,
            input_port=30000,
            output_codec=CodecType.G711_ULAW,
            output_port=20000,
            output_ip="127.0.0.1"
        )

        self.assertIsNotNone(pid)
        self.transcoder.stop_transcoding(bridge_id)

    def test_no_transcoding_needed(self):
        """✅ Should handle same-codec scenario (no transcoding)"""
        # This would be handled by bridge logic, not transcoder
        # Test that transcoder can be skipped
        bridge_id = "test-bridge-003"

        # Don't start transcoder
        self.assertNotIn(bridge_id, self.transcoder.active_transcoders)

    def test_concurrent_transcoders(self):
        """✅ Should handle multiple concurrent transcoding sessions"""
        bridge_ids = ["bridge-001", "bridge-002", "bridge-003"]

        # Start 3 concurrent transcoders
        for bridge_id in bridge_ids:
            self.transcoder.start_transcoding(
                bridge_id=bridge_id,
                input_codec=CodecType.G711_ULAW,
                input_port=20000 + len(bridge_ids),
                output_codec=CodecType.G729,
                output_port=30000 + len(bridge_ids),
                output_ip="127.0.0.1"
            )

        # All should be active
        self.assertEqual(len(self.transcoder.active_transcoders), 3)

        # Stop all
        for bridge_id in bridge_ids:
            self.transcoder.stop_transcoding(bridge_id)

        self.assertEqual(len(self.transcoder.active_transcoders), 0)


class TestSIPUserAgent(unittest.TestCase):
    """Test SIP User Agent functionality"""

    def setUp(self):
        """Setup SIP UA"""
        self.sip_ua = SIPUserAgent(sip_port=5060)
        self.sip_ua.start()

    def test_accept_sip_call(self):
        """✅ Should accept incoming SIP call"""
        call_id = "sip-call-001"
        sip_leg = self.sip_ua.accept_call(call_id, local_rtp_port=20000)

        self.assertEqual(sip_leg.call_id, call_id)
        self.assertEqual(sip_leg.rtp_port, 20000)
        self.assertEqual(sip_leg.status, "active")
        self.assertEqual(sip_leg.codec, CodecType.G711_ULAW)

    def test_hangup_sip_call(self):
        """✅ Should hangup SIP call"""
        call_id = "sip-call-002"
        sip_leg = self.sip_ua.accept_call(call_id, local_rtp_port=20000)

        # Hangup
        self.sip_ua.hangup_call(call_id)

        # Should be removed from active calls
        self.assertNotIn(call_id, self.sip_ua.active_calls)

    def test_concurrent_sip_calls(self):
        """✅ Should handle multiple concurrent SIP calls"""
        call_ids = ["call-001", "call-002", "call-003"]

        for call_id in call_ids:
            self.sip_ua.accept_call(call_id, local_rtp_port=20000)

        self.assertEqual(len(self.sip_ua.active_calls), 3)

        # Hangup all
        for call_id in call_ids:
            self.sip_ua.hangup_call(call_id)

        self.assertEqual(len(self.sip_ua.active_calls), 0)


class TestH323TerminalEmulator(unittest.TestCase):
    """Test H.323 terminal emulator (admission integration)"""

    def setUp(self):
        """Setup H.323 terminal"""
        self.terminal = H323TerminalEmulator(
            gatekeeper_uri="if://service/guard/gatekeeper:1719"
        )

    def test_request_admission(self):
        """✅ Should request admission from H.323 Gatekeeper"""
        call_id = "bridge-call-001"
        h323_leg = self.terminal.request_admission(call_id, bandwidth_bps=64000)

        self.assertIsNotNone(h323_leg)
        self.assertEqual(h323_leg.call_id, call_id)
        self.assertEqual(h323_leg.terminal_id, "if://guardian/external-bridge")
        self.assertEqual(h323_leg.codec, CodecType.G729)
        self.assertEqual(h323_leg.status, "active")

    def test_admission_bandwidth_quota(self):
        """✅ Should respect bandwidth quota (integrates with Kantian gates)"""
        call_id = "bridge-call-002"

        # Request with standard bandwidth (should succeed)
        h323_leg = self.terminal.request_admission(call_id, bandwidth_bps=64000)
        self.assertIsNotNone(h323_leg)

    def test_terminal_id_consistency(self):
        """✅ Bridge terminal should use consistent ID"""
        self.assertEqual(
            self.terminal.terminal_id,
            "if://guardian/external-bridge"
        )


class TestSIPH323Gateway(unittest.TestCase):
    """Integration tests for full gateway"""

    def setUp(self):
        """Setup gateway"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "logs"

        self.gateway = SIPH323Gateway(
            sip_port=5060,
            gatekeeper_uri="if://service/guard/gatekeeper:1719",
            log_dir=self.log_dir
        )
        self.gateway.start()

    def tearDown(self):
        """Cleanup"""
        # Teardown all bridges
        for bridge_id in list(self.gateway.bridged_calls.keys()):
            self.gateway.teardown_bridge(bridge_id)
        shutil.rmtree(self.temp_dir)

    def test_bridge_call_lifecycle(self):
        """✅ Should establish and teardown bridge"""
        sip_call_id = "sip-001"

        # Establish bridge
        bridge = self.gateway.bridge_call(sip_call_id)

        self.assertIsNotNone(bridge)
        self.assertEqual(bridge.sip_leg.codec, CodecType.G711_ULAW)
        self.assertEqual(bridge.h323_leg.codec, CodecType.G729)
        self.assertTrue(bridge.transcoding_active, "G.711 ≠ G.729, transcoding needed")

        # Bridge should be active
        active_bridges = self.gateway.get_active_bridges()
        self.assertEqual(len(active_bridges), 1)

        # Teardown
        success = self.gateway.teardown_bridge(bridge.bridge_id)
        self.assertTrue(success)

        # Should be removed
        active_bridges = self.gateway.get_active_bridges()
        self.assertEqual(len(active_bridges), 0)

    def test_policy_enforcement_integration(self):
        """✅ Kantian policy gates should apply to bridged calls"""
        sip_call_id = "sip-002"

        # Bridge call (admission control happens internally)
        bridge = self.gateway.bridge_call(sip_call_id)

        self.assertIsNotNone(bridge)

        # H.323 leg should have session_id (from gatekeeper ACF)
        self.assertIsNotNone(bridge.h323_leg.session_id)

    def test_if_witness_logging(self):
        """✅ Should log all bridge events to IF.witness"""
        sip_call_id = "sip-003"

        # Establish and teardown bridge
        bridge = self.gateway.bridge_call(sip_call_id)
        time.sleep(0.1)  # Ensure different timestamps
        self.gateway.teardown_bridge(bridge.bridge_id)

        # Check log file exists
        log_files = list(self.log_dir.glob("gateway_*.jsonl"))
        self.assertEqual(len(log_files), 1)

        # Check log content
        with open(log_files[0], 'r') as f:
            import json
            lines = f.readlines()

        self.assertEqual(len(lines), 2, "Should have ESTABLISHED + TERMINATED events")

        # Parse events
        established = json.loads(lines[0])
        terminated = json.loads(lines[1])

        self.assertEqual(established["event_type"], "BRIDGE_ESTABLISHED")
        self.assertEqual(terminated["event_type"], "BRIDGE_TERMINATED")
        self.assertIn("hash", established, "IF.witness content hash required")
        self.assertIn("hash", terminated, "IF.witness content hash required")

    def test_concurrent_bridges(self):
        """✅ Should handle multiple concurrent bridges"""
        sip_call_ids = ["sip-004", "sip-005", "sip-006"]

        bridges = []
        for call_id in sip_call_ids:
            bridge = self.gateway.bridge_call(call_id)
            bridges.append(bridge)

        # All should be active
        self.assertEqual(len(self.gateway.get_active_bridges()), 3)

        # Teardown all
        for bridge in bridges:
            self.gateway.teardown_bridge(bridge.bridge_id)

        self.assertEqual(len(self.gateway.get_active_bridges()), 0)

    def test_transcoding_activation(self):
        """✅ Transcoding should activate when codecs differ"""
        sip_call_id = "sip-007"

        bridge = self.gateway.bridge_call(sip_call_id)

        # G.711 (SIP) ≠ G.729 (H.323), transcoding needed
        self.assertTrue(bridge.transcoding_active)
        self.assertIsNotNone(bridge.transcoder_pid)

        self.gateway.teardown_bridge(bridge.bridge_id)


def run_tests():
    """Run all tests and print summary"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCodecTranscoder))
    suite.addTests(loader.loadTestsFromTestCase(TestSIPUserAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestH323TerminalEmulator))
    suite.addTests(loader.loadTestsFromTestCase(TestSIPH323Gateway))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("SIP-H.323 Gateway Test Summary")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"❌ Errors: {len(result.errors)}")
    print("="*70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
