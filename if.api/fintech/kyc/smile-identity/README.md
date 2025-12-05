# Smile Identity REST API Adapter

Python adapter for Smile Identity's REST API, providing a thin, configurable
wrapper around common KYC workflows (ID verification and job status checks)
and integrating with the InfraFabric IF.bus patterns.

**Status:** Implementing  
**Integration Type:** REST API (server-side)  
**Reference:** https://docs.usesmileid.com/integration-options/rest-api

---

## Overview

The Smile Identity REST adapter focuses on:

- Submitting KYC jobs (e.g. ID verification)
- Checking job status and retrieving results
- Handling request signing (HMAC) and authentication
- Providing a clean, dataclass-based interface for application code

It does **not** aim to cover every Smile Identity feature; instead it offers a
solid starting point that can be extended as needed.

---

## Quick Start

```python
from smile_identity_adapter import (
    SmileIdentityAdapter,
    JobType,
    IDInfo,
)

adapter = SmileIdentityAdapter(
    partner_id="your_partner_id",
    api_key="your_api_key",
    base_url="https://testapi.smileidentity.com",
)

# Submit a basic ID verification job
job = adapter.submit_id_verification(
    job_type=JobType.BASIC_KYC,
    user_id="user-123",
    id_info=IDInfo(
        country="NG",
        id_type="BVN",
        id_number="12345678901",
        first_name="Jane",
        last_name="Doe",
    ),
)

print("Job submitted:", job["job_id"])

# Later: check status
status = adapter.get_job_status(job_id=job["job_id"], user_id="user-123")
print("Job status:", status["status"])
```

---

## Configuration Notes

- `base_url` should be set to the appropriate Smile Identity environment:
  - Sandbox: `https://testapi.smileidentity.com`
  - Production: consult official Smile Identity documentation
- The adapter expects a valid `partner_id` and `api_key` as issued by Smile
  Identity. The exact authentication mechanism (e.g. server token) can be
  extended in the code as needed.

