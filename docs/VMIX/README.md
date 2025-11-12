# IF.vmix - vMix Integration Documentation

**Professional live video production control from the command line**

---

## Overview

IF.vmix provides complete CLI control for vMix professional video production software, integrated with InfraFabric's IF.witness logging for audit trails.

**Key Features:**
- Dead-simple CLI interface for production engineers
- Full production control (cut, fade, transitions, overlays)
- NDI source management
- Streaming and recording control
- PTZ camera control
- Audio management
- Complete IF.witness integration
- Shell completion (bash/zsh)
- Multi-instance support

---

## Documentation

### Getting Started
- **[CLI Interface Guide](cli-interface.md)** - Complete user guide with installation, configuration, and all commands
- **[Quick Reference](QUICK-REFERENCE.md)** - Cheat sheet for production (print this!)

### For Developers
- Source code: `/home/user/infrafabric/src/vmix/`
- CLI commands: `/home/user/infrafabric/src/cli/vmix_commands.py`
- Tests: `/home/user/infrafabric/tests/test_vmix_cli.py`
- Completions: `/home/user/infrafabric/completions/`

---

## Quick Start

```bash
# 1. Add vMix instance
if vmix add myvmix --host 192.168.1.100

# 2. Test connection
if vmix test myvmix

# 3. Control production
if vmix cut myvmix --input 1
if vmix fade myvmix --input 2
if vmix status myvmix
```

---

## Architecture

### Components

```
IF.vmix/
├── src/vmix/
│   ├── __init__.py          # Module exports
│   ├── client.py            # VMixClient - REST API + XML status
│   ├── config.py            # VMixConfig - Instance management
│   └── models.py            # Data models (VMixInstance, VMixStatus, etc.)
├── src/cli/
│   └── vmix_commands.py     # Click-based CLI commands
├── tests/
│   └── test_vmix_cli.py     # Unit and integration tests
├── completions/
│   ├── vmix-completion.bash # Bash completion
│   └── vmix-completion.zsh  # Zsh completion
└── docs/VMIX/
    ├── cli-interface.md     # Complete user guide
    ├── QUICK-REFERENCE.md   # Cheat sheet
    └── README.md            # This file
```

### Data Flow

```
CLI Command → VMixConfig (load instance) → VMixClient (API call) → vMix API
                                                    ↓
                                            IF.witness (log operation)
```

### Configuration Storage

- **Location:** `~/.if/vmix/instances.yaml`
- **Format:** YAML
- **Contents:** Instance configurations (name, host, port, added_at)

### Logging

- **Component:** IF.vmix
- **Storage:** IF.witness database (`~/.if-witness/witness.db`)
- **Format:** Hash-chained, signed entries
- **Includes:** All operations (cut, fade, stream, record, etc.)

---

## Command Groups

### Connection Management
- `add` - Add vMix instance
- `list` - List instances
- `test` - Test connection
- `remove` - Remove instance

### Production Control
- `cut` - Instant cut to input
- `fade` - Fade to input
- `preview` - Set preview input
- `transition` - Custom transition
- `overlay` - Set overlay input

### NDI Control
- `ndi add` - Add NDI source
- `ndi list` - List NDI inputs
- `ndi remove` - Remove input

### Streaming
- `stream start` - Start streaming
- `stream stop` - Stop streaming
- `stream status` - Get streaming status

### Recording
- `record start` - Start recording
- `record stop` - Stop recording
- `record status` - Get recording status

### Status & Queries
- `status` - Get vMix status
- `inputs` - List all inputs
- `state` - Get production state

### PTZ Camera Control
- `ptz move` - Move PTZ camera
- `ptz preset` - Recall preset
- `ptz home` - Home position

### Audio Control
- `audio volume` - Set volume
- `audio mute` - Mute audio
- `audio unmute` - Unmute audio

---

## vMix API Integration

IF.vmix uses the vMix Function API and XML Status API:

**Function API:** HTTP GET requests to execute commands
```
http://vmix-ip:8088/api/?Function=Cut&Input=1
```

**XML Status API:** HTTP GET request for system status
```
http://vmix-ip:8088/api/
```

**Official Documentation:**
https://www.vmix.com/help25/index.htm?DeveloperAPI.html

---

## IF.witness Integration

Every vMix operation is logged to IF.witness with:
- Event type (e.g., `vmix_cut`, `vmix_fade`)
- Component (`IF.vmix`)
- Trace ID (unique per operation)
- Payload (instance, operation, params, result)
- Timestamp
- Hash chain link
- Ed25519 signature

**Query logs:**
```bash
if witness query --component IF.vmix
if witness query --event vmix_cut
if witness export --component IF.vmix --format csv
```

---

## Philosophy

IF.vmix follows InfraFabric principles:

**IF.ground Principle 8:** Observability without fragility
- Every operation logged
- No performance impact on production
- Tamper-proof audit trails

**Production Engineers First:**
- Dead-simple CLI commands
- Clear, descriptive output
- No magic, transparent operations
- Tab completion for speed
- Aliases and scripting support

**Reliability:**
- Graceful error handling
- Connection testing
- Clear error messages
- Non-blocking logging (failures don't stop operations)

---

## Requirements

### Software
- Python 3.10+
- vMix 25.0+ (with Web Controller enabled)
- Network access to vMix host

### Python Dependencies
- click >= 8.1.0
- requests >= 2.31.0
- PyYAML >= 6.0.0
- cryptography >= 41.0.0 (for IF.witness)

---

## Installation

```bash
# Clone repository
git clone https://github.com/yourorg/infrafabric
cd infrafabric

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .

# Verify installation
if vmix --help
```

---

## Testing

```bash
# Run all tests
pytest tests/test_vmix_cli.py -v

# Run specific test
pytest tests/test_vmix_cli.py::TestVMixClient::test_get_status -v

# Run with coverage
pytest tests/test_vmix_cli.py --cov=vmix --cov-report=html
```

### Test Coverage
- VMixClient API operations
- VMixConfig instance management
- Data model serialization
- CLI command execution
- IF.witness logging integration
- Error handling

---

## Examples

### Basic Production Control
```bash
if vmix add studio1 --host 192.168.1.100
if vmix cut studio1 --input 1
if vmix fade studio1 --input 2 --duration 2000
```

### Automated Show Script
```bash
#!/bin/bash
if vmix cut studio1 --input 1
sleep 5
if vmix fade studio1 --input 2 --duration 2000
sleep 10
if vmix overlay studio1 --num 1 --input 5
```

### Multi-Instance Control
```bash
if vmix add main --host 192.168.1.100
if vmix add backup --host 192.168.1.101
if vmix cut main --input 1 & if vmix cut backup --input 1 & wait
```

---

## Support & Contributing

### Get Help
- **Documentation:** Read [cli-interface.md](cli-interface.md)
- **Quick Reference:** See [QUICK-REFERENCE.md](QUICK-REFERENCE.md)
- **GitHub Issues:** https://github.com/yourorg/infrafabric/issues
- **Discord:** https://discord.gg/infrafabric

### Contributing
1. Read [CONTRIBUTING.md](../../CONTRIBUTING.md)
2. Create feature branch
3. Write tests
4. Submit pull request

### Bug Reports
Include:
- IF.vmix version
- vMix version
- Command that failed
- Error message
- IF.witness logs

---

## Roadmap

### Current (v1.0)
- ✅ Full production control
- ✅ NDI source management
- ✅ Streaming/recording control
- ✅ PTZ camera control
- ✅ Audio control
- ✅ IF.witness integration
- ✅ Shell completion
- ✅ Comprehensive tests

### Future
- Auto-discovery via mDNS
- WebSocket API support (real-time status)
- Macro support (saved command sequences)
- GUI dashboard
- Multi-instance synchronization
- Preset management

---

## License

MIT License - See [LICENSE](../../LICENSE)

---

## Credits

Built with ❤️ for production engineers

Part of the InfraFabric project:
- **IF.witness** - Tamper-proof logging
- **IF.ground** - Philosophy and principles
- **IF.bus** - Real-time communication (planned)

---

*"Dead-simple tools for complex production workflows"*

---

**Session 5 (CLI) - vMix Integration Sprint**
*Delivered: 2025-11-12*
