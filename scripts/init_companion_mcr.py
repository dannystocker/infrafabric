#!/usr/bin/env python3
"""
Initialize Companion MCR Bridge in Redis

Bootstraps the bridge configuration, core protocols, and example data.

Usage:
    python scripts/init_companion_mcr.py [--redis-url REDIS_URL]
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import redis.asyncio as aioredis
from infrafabric.integrations.companion import (
    CompanionBridgeConfig,
    ProtocolTemplate,
    CompanionDevice,
    IntentMapping,
    ButtonAction,
    CompanionMacro,
    MacroStep,
)


async def initialize_companion_mcr(redis_url: str):
    """Bootstrap Companion MCR bridge configuration"""

    print(f"Connecting to Redis: {redis_url}")
    redis_client = await aioredis.from_url(redis_url, decode_responses=True)

    try:
        # Test connection
        await redis_client.ping()
        print("✓ Connected to Redis")

        # 1. Bridge configuration
        print("\n1. Creating bridge configuration...")
        config = CompanionBridgeConfig(
            host="localhost",
            port=8888,
            protocol="http",
            timeout_ms=5000,
            retry_attempts=3,
            retry_backoff_ms=1000,
            enable_state_tracking=True,
            enable_macros=True,
        )
        await redis_client.set("mcr:bridge:companion:config", config.to_redis())
        print(f"   ✓ Bridge config: {config.base_url}")

        # 2. Core protocols
        print("\n2. Registering core protocols...")
        protocols = [
            ProtocolTemplate(
                protocol_name="press",
                protocol_type="http",
                template="/api/location/{page}/{row}/{col}/press",
                method="POST",
                variables=["page", "row", "col"],
                description="Press button on specified page/row/col",
            ),
            ProtocolTemplate(
                protocol_name="set_text",
                protocol_type="http",
                template="/api/location/{page}/{row}/{col}/style",
                method="PUT",
                variables=["page", "row", "col", "text"],
                description="Update button text label",
            ),
            ProtocolTemplate(
                protocol_name="osc_trigger",
                protocol_type="osc",
                template="/companion/button/{page}/{button}/press",
                variables=["page", "button"],
                osc_port=12345,
                description="Send OSC trigger to Companion",
            ),
        ]

        for proto in protocols:
            await redis_client.set(
                f"mcr:protocol:companion:{proto.protocol_name}", proto.to_redis()
            )
            print(f"   ✓ Protocol: {proto.protocol_name} ({proto.protocol_type})")

        # 3. Example devices
        print("\n3. Registering example devices...")
        devices = [
            CompanionDevice(
                device_id="studio_main",
                device_type="streamdeck_xl",
                rows=8,
                cols=8,
                metadata={
                    "location": "Control Room A",
                    "serial": "CL09H1A01234",
                },
            ),
            CompanionDevice(
                device_id="control_room_b",
                device_type="xtouch_mini",
                rows=2,
                cols=8,
                page_count=5,
                metadata={
                    "location": "Control Room B",
                    "serial": "XTM987654321",
                },
            ),
        ]

        for device in devices:
            await redis_client.set(
                f"mcr:catalog:companion:device:{device.device_id}", device.to_redis()
            )
            print(
                f"   ✓ Device: {device.device_id} ({device.rows}x{device.cols} buttons)"
            )

        # 4. Example intents
        print("\n4. Creating example intents...")
        intents = [
            IntentMapping(
                intent_name="studio_dark_mode",
                description="Enable dark mode studio lighting",
                actions=[
                    ButtonAction(
                        action_type="press",
                        protocol_name="press",
                        device_id="studio_main",
                        variables={"page": 1, "row": 0, "col": 0},
                    ),
                    ButtonAction(
                        action_type="set_text",
                        protocol_name="set_text",
                        device_id="studio_main",
                        variables={"page": 1, "row": 0, "col": 0, "text": "DARK"},
                        delay_ms=500,
                    ),
                ],
                priority=1,
                created_by="if.sam",
            ),
            IntentMapping(
                intent_name="emergency_lights",
                description="Activate emergency lighting system",
                actions=[
                    ButtonAction(
                        action_type="press",
                        protocol_name="press",
                        device_id="studio_main",
                        variables={"page": 0, "row": 7, "col": 7},
                    )
                ],
                priority=10,
                created_by="if.guard",
            ),
        ]

        for intent in intents:
            await redis_client.set(
                f"mcr:mapping:companion:intent:{intent.intent_name}", intent.to_redis()
            )
            print(
                f"   ✓ Intent: {intent.intent_name} ({len(intent.actions)} actions)"
            )

        # 5. Example macro
        print("\n5. Creating example macro...")
        macro = CompanionMacro(
            macro_id="morning_startup",
            macro_name="Morning Studio Startup",
            description="Initialize studio for morning broadcast",
            steps=[
                MacroStep(
                    step_number=1,
                    intent_name="studio_power_on",
                    wait_for_completion=True,
                    timeout_ms=5000,
                    on_failure="abort",
                ),
                MacroStep(
                    step_number=2,
                    intent_name="studio_dark_mode",
                    wait_for_completion=True,
                    timeout_ms=3000,
                    on_failure="continue",
                ),
            ],
            created_by="if.sam",
        )
        await redis_client.set(
            f"mcr:companion:macro:{macro.macro_id}", macro.to_redis()
        )
        print(f"   ✓ Macro: {macro.macro_name} ({len(macro.steps)} steps)")

        print("\n" + "=" * 70)
        print("✓ Companion MCR bridge initialized successfully!")
        print("=" * 70)
        print("\nNext steps:")
        print("1. Start Companion on localhost:8888")
        print("2. Run test script: python scripts/test_companion_mcr.py")
        print("3. Check Redis keys: redis-cli KEYS 'mcr:*'")
        print("\nRegistered resources:")
        print(f"  - Protocols: {len(protocols)}")
        print(f"  - Devices: {len(devices)}")
        print(f"  - Intents: {len(intents)}")
        print(f"  - Macros: 1")

    finally:
        await redis_client.close()


def main():
    parser = argparse.ArgumentParser(
        description="Initialize Companion MCR Bridge in Redis"
    )
    parser.add_argument(
        "--redis-url",
        default="redis://localhost:6379",
        help="Redis connection URL (default: redis://localhost:6379)",
    )

    args = parser.parse_args()

    try:
        asyncio.run(initialize_companion_mcr(args.redis_url))
    except Exception as e:
        print(f"\n✗ Initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
