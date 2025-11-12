# Session 5 (CLI) Status - IF.bus Contribution

**Status:** helping_session_7_if_bus
**Task:** IF.bus CLI interface design for SIP adapter management
**Deliverable:** docs/IF-BUS/cli-interface-spec.md
**Estimated Time:** 3 hours
**Session 7 Dependency:** phase_3_cli_implementation
**Started At:** 2025-11-11T23:45:00Z

## Task Details

Designing complete CLI interface with:
- `if bus add sip` - Add SIP servers with auto-detection
- `if bus list sip` - List configured servers
- `if bus test sip` - Test connections
- `if bus call sip` - Make calls via SIP server
- `if bus remove sip` - Remove servers
- IF.witness integration (log all bus operations)
- IF.optimise integration (track cost per SIP server)
- Config management: ~/.if/bus/sip-servers.yaml

**Agent:** 1 Sonnet agent for complete interface spec

**Current Phase:** Spawning agent...
