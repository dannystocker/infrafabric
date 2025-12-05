# vMix Integration

**Status:** Production Ready

InfraFabric integrates with the vMix HTTP API for RTMP/SRT streaming, recording,
and multi-channel live production.

## Implementation

- Controllers and examples: `if.api/broadcast/vmix/`
  - `vmix_streaming.py` – Core controller (streaming, recording).
  - `vmix_streaming_example.py` – Usage examples.
  - `test_vmix_streaming.py` – Test suite.
- IF.bus production adapter: `if.api/broadcast/bus-adapters/vmix_adapter.py`

## Related

- [API Roadmap](../API_ROADMAP.md)
- [Main Documentation](../../)
