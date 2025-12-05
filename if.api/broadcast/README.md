# if.api/broadcast – Broadcast & Streaming Adapters

This directory contains InfraFabric's broadcast integrations, focused on live
video production and IF.bus event integration.

## Structure

```
if.api/broadcast/
├── vmix/          # vMix HTTP API controllers (streaming, examples, tests)
├── obs/           # OBS WebSocket controllers (streaming, examples, tests)
└── bus-adapters/  # IF.bus production adapters (vMix, OBS, Home Assistant)
```

- `vmix/` – Direct vMix controllers (`vmix_streaming.py`, examples, tests).
- `obs/` – Direct OBS controllers (`obs_streaming.py`, demos, tests).
- `bus-adapters/` – Unified IF.bus production adapters:
  - `vmix_adapter.py` – vMix IF.bus adapter.
  - `obs_adapter.py` – OBS IF.bus adapter.
  - `ha_adapter.py` – Home Assistant IF.bus adapter.
  - `production_adapter_base.py` – Shared adapter base class and events.

For the canonical IF.bus broadcast integration paths:

- vMix: `if.api.broadcast.bus-adapters.vmix_adapter`
- OBS: `if.api.broadcast.bus-adapters.obs_adapter`

