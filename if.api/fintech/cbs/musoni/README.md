# Musoni Core Banking API Adapter

Python adapter for Musoni Core Banking System integration with the InfraFabric
platform. Musoni exposes a Fineract-compatible REST API, so this adapter
follows the same patterns as the Mifos/Fineract adapter while keeping Musoni
specific configuration separate.

**Status:** Implementing  
**Compatibility:** Musoni Core Banking (Fineract-style REST API)  
**Citation:** `if://adapter/fintech/musoni-cbs/v1`

---

## Overview

The Musoni adapter is designed for MFIs and digital lenders running on the
Musoni CBS platform. It focuses on:

- Client lifecycle (create, search, retrieve, update)
- Loan lifecycle (submit, approve, disburse, post repayment)
- Basic savings and group support (where exposed via Musoni API)
- IF.bus-compatible event emission hooks

Internally the adapter mirrors the Mifos/Fineract adapter structure so that
migration between Musoni and Fineract can reuse most of the workflow code.

---

## Installation

```bash
pip install requests>=2.25.0
```

Or as part of the full InfraFabric API stack:

```bash
pip install -r /home/setup/infrafabric/if.api/requirements.txt
```

---

## Quick Start

```python
from musoni_adapter import (
    MusoniAdapter,
    MusoniClientData,
    MusoniLoanApplicationData,
)

adapter = MusoniAdapter(
    base_url="https://api.musonisystem.com",
    username="api-user",
    password="api-password",
    tenant_id="default"  # optional, if your Musoni instance uses tenants
)

# Verify connection
if adapter.verify_connection():
    print("Connected to Musoni")

# Create a client
client = MusoniClientData(
    first_name="Jane",
    last_name="Kipchoge",
    phone_number="+254712345678",
    external_id="MUSONI-CLIENT-001",
)

result = adapter.create_client(client)
print(f"Client created with ID: {result['client_id']}")
```

---

## Notes

- Endpoints assume a Fineract-style Musoni deployment (`/api/v1/...`). If your
  instance uses different paths or a gateway, override `base_url` accordingly.
- This adapter is intentionally conservative and focuses on core flows; it can
  be extended with additional endpoints as needed.

