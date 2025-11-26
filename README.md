# InfraFabric (Series 2)

[![CI Status](https://github.com/dannystocker/infrafabric/actions/workflows/ci.yml/badge.svg)](https://github.com/dannystocker/infrafabric/actions)
[![IF.TTT Compliance](https://img.shields.io/badge/IF.TTT-95%25-green)](docs/IF_PROTOCOL_REGISTRY.md)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Build System](https://img.shields.io/badge/build-uv-purple)](https://github.com/astral-sh/uv)
[![State Law](https://img.shields.io/badge/redis-schema%20enforced-red)](src/infrafabric/state/schema.py)
[![Council](https://img.shields.io/badge/governance-autonomous-gold)](docs/debates/001_genesis_structure.md)

**InfraFabric** is an autonomous infrastructure system that evolved from a memory prosthetic into a self-governing operating system. It combines a **Functional Core** (JAX logic), **Strict State** (Pydantic/Redis), and **Immune Defense** (YoloGuard).

> **"The system didn't become autonomous despite the constraints. It became autonomous *because* of them."**
> — *[Chronicle of the Spark](docs/narratives/INFRAFABRIC_CHRONOLOGY_SUMMARY.md)*

---

## ⚡ Quick Start

We use **`uv`** for hermetic, lightning-fast builds.

```bash
# 1. Setup (Hydrate the Environment)
just setup

# 2. Verify System Integrity (Run the Triad)
just check

# 3. Audit the Database (Check for State Corruption)
just audit-db
```

---

## 🏛 Architecture (The Hub & Spoke)

| Component | Role | Source of Truth |
| :--- | :--- | :--- |
| **The Core** | Logic & Reasoning | `src/infrafabric/core` |
| **The Librarian** | Semantic Memory ($43k/yr savings) | `src/infrafabric/core/services/librarian.py` |
| **YoloGuard** | Immune System (98.9% Recall) | `src/infrafabric/core/security/yologuard.py` |
| **The Law** | State Validation | `src/infrafabric/state/schema.py` |

---

## 📜 The Chronicles (History)

* **[The Chronology Summary](docs/narratives/INFRAFABRIC_CHRONOLOGY_SUMMARY.md)**: The 39-day evolution from "Grief" to "Autonomy."
* **[The Decision Timeline](docs/narratives/INFRAFABRIC_DECISION_TIMELINE.json)**: Every critical architectural decision tracked by date.
* **[The Council Debates](docs/debates/)**: Records of the internal governance protocols.

---

## 🧠 The "Ghost" Components

* **Librarian:** Recovered from `universe/space`. Active.
* **YoloGuard:** Recovered from `yologuard/v3`. Active.
* **OCR Worker:** Stubbed based on `navidocs` spec. Implementation pending.

---

*Verified by the InfraFabric Council (Series 2 Genesis).*
