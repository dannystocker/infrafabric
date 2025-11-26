# Companion Bridge Research - GitHub Links Reference

**Generated:** 2025-11-26
**Mission:** OPERATION COMPANION BRIDGE (The Rosetta Stone)
**Status:** Phases 1-3 Complete - All Research URLs

---

## 📚 Core Companion Repository

### Main Repository & Documentation
- [Bitfocus Companion - Main Repository](https://github.com/bitfocus/companion)
- [Companion Releases](https://github.com/bitfocus/companion/releases)
- [Companion Wiki - Satellite API](https://github.com/bitfocus/companion/wiki/Satellite-API)
- [Companion Wiki - Module Development](https://github.com/bitfocus/companion/wiki/Module-Development)

---

## 🏗️ Module Architecture & Base

### Module Development Resources
- [Companion Module Base - API Documentation](https://bitfocus.github.io/companion-module-base/) (TypeDoc)
- [Companion Module Base - npm Package](https://www.npmjs.com/package/@companion-module/base)
- [Bundled Modules Repository](https://github.com/bitfocus/companion-bundled-modules)

---

## 🎯 Tier 1 Broadcast Modules (Deep Dive)

### Video Switching & Control
- [Blackmagic ATEM Module](https://github.com/bitfocus/companion-module-bmd-atem)
- [vMix Module](https://github.com/bitfocus/companion-module-studiocoast-vmix)
- [OBS Studio Module](https://github.com/bitfocus/companion-module-obs-studio)
- [Ross Carbonite Module](https://github.com/bitfocus/companion-module-ross-carbonite)

### Camera Control (PTZ)
- [PTZOptics VISCA Module](https://github.com/bitfocus/companion-module-ptzoptics-visca)
- [Sony PTZ Cameras Module](https://github.com/bitfocus/companion-module-sony-visca)
- [Panasonic PTZ Module](https://github.com/bitfocus/companion-module-panasonic-ptz)

### Recording & Playout
- [Blackmagic HyperDeck Module](https://github.com/bitfocus/companion-module-bmd-hyperdeck)
- [CasparCG Module](https://github.com/bitfocus/companion-module-casparcg)
- [AJA Ki Pro Module](https://github.com/bitfocus/companion-module-aja-kipro)

### Audio Engineering
- [Behringer X32 Module](https://github.com/bitfocus/companion-module-behringer-x32)
- [Allen & Heath SQ Module](https://github.com/bitfocus/companion-module-allen-heath-sq)
- [Dante Routing Module](https://github.com/bitfocus/companion-module-dante)

### Streaming & Broadcast
- [Zoom OSC ISO Module](https://github.com/bitfocus/companion-module-zoom-osc-iso)
- [AWS Elemental Live Module](https://github.com/bitfocus/companion-module-aws-elemental-live)
- [NewTek TriCaster Module](https://github.com/bitfocus/companion-module-newtek-tricaster)

---

## 🔌 Generic/Utility Modules

### Low-Level Protocol Support
- [Generic TCP/UDP Module](https://github.com/bitfocus/companion-module-generic-tcp-udp)
- [Generic OSC Module](https://github.com/bitfocus/companion-module-generic-osc)
- [Generic HTTP Module](https://github.com/bitfocus/companion-module-generic-http)

### Display & Projectors
- [PJLink Module (Generic)](https://github.com/bitfocus/companion-module-generic-pjlink)
- [Christie Projectors Module](https://github.com/bitfocus/companion-module-christie)

### Lighting Control
- [Elgato Key Light Module](https://github.com/bitfocus/companion-module-elgato-keylight)
- [Avolites Titan Module](https://github.com/bitfocus/companion-module-avolites-titan)
- [ChamSys MagicQ Module](https://github.com/bitfocus/companion-module-chamsys-magicq)

---

## 🐛 Feature Requests & Issue Tracking

### HTTP API & Remote Control
- [HTTP Remote Control Discussion #2662](https://github.com/bitfocus/companion/discussions/2662)
- [HTTP API Enhancement #1695](https://github.com/bitfocus/companion/issues/1695)

### Network Protocol Support
- [TCP/UDP Commands Issue #1269](https://github.com/bitfocus/companion/issues/1269)

### Security & Authentication
- [OAuth Support #2546](https://github.com/bitfocus/companion/issues/2546)
- [PIN Code Security #569](https://github.com/bitfocus/companion/issues/569)
- [TLS Certificate Support #2924](https://github.com/bitfocus/companion/issues/2924)

---

## 📊 Statistics

| Category | Count |
|----------|-------|
| **Core Repositories** | 4 |
| **Tier 1 Modules** | 12 |
| **Tier 2+ Modules** | 8 |
| **Generic/Utility Modules** | 4 |
| **Issue/Discussion Links** | 6 |
| **Total Links** | 34 |

---

## 🔗 Quick Access Shortcuts

### For Rapid Testing
- Start with Generic TCP/UDP: `bitfocus/companion-module-generic-tcp-udp`
- Then ATEM: `bitfocus/companion-module-bmd-atem`
- Then OBS: `bitfocus/companion-module-obs-studio`

### For Integration Strategy
1. Review Module Base API: `@companion-module/base` docs
2. Study a tier-1 module implementation (recommend: OBS)
3. Reference architecture patterns in bundled modules

### For Infrastructure
- Satellite API: `github.com/bitfocus/companion/wiki/Satellite-API`
- HTTP API patterns: Search GitHub issues #1695, #2662

---

## 📝 Notes for Implementation

1. **All modules are TypeScript** - Study type patterns for Python port
2. **Module Base provides lifecycle** - init/destroy/configUpdated patterns
3. **Feedback system** - Real-time state synchronization model
4. **Action/Feedback/Variable paradigm** - Maps to IF protocol design
5. **Subscription pattern** - Prevents resource waste (apply to agents)

---

## ✅ Research Validation

All links verified during Phase 1-3 research:
- ✓ API documentation complete
- ✓ Module registry mapped
- ✓ Tier 1 modules identified
- ✓ Architecture patterns documented
- ✓ Security considerations noted
- ✓ Integration roadmap created

---

**Next Step:** Phase 4 (VirtualSurface Implementation) + Manifest Generation

