#!/usr/bin/env python3
"""
Test Companion MCR Bridge

Simple test script to verify bridge functionality.

Prerequisites:
    1. Run init_companion_mcr.py first
    2. Start Companion on localhost:8888
    3. Have Redis running

Usage:
    python scripts/test_companion_mcr.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from infrafabric.integrations.companion import CompanionBridge, CompanionError


async def test_intent_execution():
    """Test basic intent execution"""
    print("\n" + "=" * 70)
    print("TEST: Intent Execution")
    print("=" * 70)

    try:
        async with CompanionBridge() as bridge:
            # Test intent that should exist (created by init script)
            print("\n1. Executing intent: studio_dark_mode")
            result = await bridge.execute_intent("studio_dark_mode")

            if result.success:
                print(f"   ✓ Success!")
                print(f"   - Actions executed: {result.actions_executed}")
                print(f"   - Latency: {result.latency_ms:.1f}ms")
            else:
                print(f"   ✗ Failed: {result.error}")

    except CompanionError as e:
        print(f"   ✗ Error: {e.error_type.value} - {e.message}")
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")


async def test_missing_intent():
    """Test error handling for missing intent"""
    print("\n" + "=" * 70)
    print("TEST: Missing Intent Error Handling")
    print("=" * 70)

    try:
        async with CompanionBridge() as bridge:
            print("\n1. Executing non-existent intent: fake_intent")
            result = await bridge.execute_intent("fake_intent")

            if not result.success:
                print(f"   ✓ Correctly failed")
                print(f"   - Error type: {result.error.error_type.value}")
                print(f"   - Message: {result.error.message}")
            else:
                print(f"   ✗ Should have failed!")

    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")


async def test_macro_execution():
    """Test macro execution"""
    print("\n" + "=" * 70)
    print("TEST: Macro Execution")
    print("=" * 70)

    try:
        async with CompanionBridge() as bridge:
            print("\n1. Executing macro: morning_startup")
            result = await bridge.execute_macro("morning_startup")

            print(f"   - Success: {result.success}")
            print(f"   - Steps completed: {result.metadata.get('steps_completed', 0)}")
            print(f"   - Steps failed: {result.metadata.get('steps_failed', 0)}")

            if result.success:
                print("   ✓ Macro completed")
            else:
                print("   ⚠ Macro had failures (expected - intents may not exist)")

    except Exception as e:
        print(f"   ⚠ Error: {e} (expected if intents don't exist)")


async def test_device_registration():
    """Test device registration"""
    print("\n" + "=" * 70)
    print("TEST: Device Registration")
    print("=" * 70)

    try:
        from infrafabric.integrations.companion import CompanionDevice

        async with CompanionBridge() as bridge:
            print("\n1. Registering test device: test_device")
            device = CompanionDevice(
                device_id="test_device",
                device_type="virtual",
                rows=4,
                cols=4,
                metadata={"test": True},
            )
            await bridge.register_device(device)
            print("   ✓ Device registered")

            # Verify device was stored
            retrieved = await bridge._get_device("test_device")
            if retrieved and retrieved.device_id == "test_device":
                print("   ✓ Device retrieved from Redis")
            else:
                print("   ✗ Device not found in Redis")

    except Exception as e:
        print(f"   ✗ Error: {e}")


async def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("COMPANION MCR BRIDGE TEST SUITE")
    print("=" * 70)
    print("\nNote: Some tests may fail if Companion is not running.")
    print("This is expected. We're testing the bridge logic, not Companion itself.")

    # Run tests
    await test_intent_execution()
    await test_missing_intent()
    await test_macro_execution()
    await test_device_registration()

    print("\n" + "=" * 70)
    print("TEST SUITE COMPLETE")
    print("=" * 70)
    print("\nIf you see connection errors, that's normal if Companion isn't running.")
    print("The bridge should handle errors gracefully with retry logic.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n✗ Test suite failed: {e}")
        sys.exit(1)
