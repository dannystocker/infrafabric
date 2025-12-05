# Fintech Adapters & Debugging

InfraFabric's African fintech adapters live under `if.api/fintech/` and cover
mobile money, CBS (core banking), KYC/CRB, and messaging providers.

This page summarizes the main adapters and documents the shared debug
utilities you can enable when troubleshooting integrations.

## Fintech Adapters Overview

| Category      | Adapter           | Path                                          | Example Script                                             |
|--------------|-------------------|-----------------------------------------------|------------------------------------------------------------|
| CBS          | Mifos/Fineract    | `if.api/fintech/cbs/mifos/`                   | `if.api/fintech/cbs/mifos/example_usage.py`                |
| CBS          | Musoni            | `if.api/fintech/cbs/musoni/`                  | `if.api/fintech/cbs/musoni/example_usage.py`               |
| KYC / CRB    | TransUnion Africa | `if.api/fintech/kyc/transunion/`              | `if.api/fintech/kyc/transunion/example_usage.py`           |
| KYC / ID     | Smile Identity    | `if.api/fintech/kyc/smile-identity/`          | `if.api/fintech/kyc/smile-identity/example_usage.py`       |
| Messaging    | Africa's Talking  | `if.api/fintech/messaging/africas-talking/`   | `if.api/fintech/messaging/africas-talking/example_usage.py`|
| Mobile Money | M-Pesa            | `if.api/fintech/mobile-money/mpesa/`          | `if.api/fintech/mobile-money/mpesa/examples.py`            |
| Mobile Money | MTN MoMo          | `if.api/fintech/mobile-money/mtn-momo/`       | `if.api/fintech/mobile-money/mtn-momo/example_usage.py`    |
| Mobile Money | Airtel Money      | `if.api/fintech/mobile-money/airtel-money/`   | `if.api/fintech/mobile-money/airtel-money/example_usage.py`|
| Mobile Money | Orange Money      | `if.api/fintech/mobile-money/orange-money/`   | `if.api/fintech/mobile-money/orange-money/example_usage.py`|

CBS, KYC, messaging, and mobile money adapters with centralized HTTP
helpers are already wired into the shared debug utilities described below.

---

## Shared Fintech Debug Utilities

**Module:** `fintech_debug_utils.py` (project root)

Exports:

- `fintech_debug_enabled(provider: Optional[str]) -> bool`
- `ft_debug_log_request(logger, provider, url, payload)`
- `ft_debug_log_response(logger, provider, status_code, body_text)`

Adapters that use a central `_make_request` / `_request` helper call these
functions so you can enable detailed request/response logging without
touching business logic.

### Environment Flags

Debug is controlled via environment variables:

- Global flag for all fintech adapters:

```bash
export IF_FINTECH_DEBUG=1
```

- Per-adapter flags (override or complement the global flag):

```bash
export IF_FINTECH_DEBUG_MIFOS=1
export IF_FINTECH_DEBUG_MUSONI=1
export IF_FINTECH_DEBUG_TRANSUNION=1
export IF_FINTECH_DEBUG_SMILE_IDENTITY=1
export IF_FINTECH_DEBUG_AFRICAS_TALKING=1
export IF_FINTECH_DEBUG_MPESA=1
export IF_FINTECH_DEBUG_MTN_MOMO=1
export IF_FINTECH_DEBUG_AIRTEL_MONEY=1
export IF_FINTECH_DEBUG_ORANGE_MONEY=1
```

When enabled, the adapter logs:
- Outgoing URL and JSON/body payload (truncated to a safe length).
- Incoming HTTP status code and response body preview.

To apply **automatic secret redaction** using IF.yologuard via
`if.armour.secrets.detect`, you can additionally set:

```bash
export IF_DEBUG_REDACT=1                 # Global redaction for all debug logs
export IF_FINTECH_DEBUG_REDACT=1         # Redaction for all fintech debug logs
export IF_FINTECH_DEBUG_REDACT_MPESA=1   # Redaction only for M-Pesa logs
```

These flags cause `fintech_debug_utils` to pass payloads and response
snippets through `SecretRedactorV3` before logging, so credentials and
other high-risk secrets are scrubbed while retaining enough context for
troubleshooting. This is intended for controlled debugging environments,
not general production use.

---

## CLI Usage: `-d/-v/--debug/--verbose`

Several fintech adapters ship with example scripts that can be run directly.
These scripts now support consistent CLI flags:

- `-d`, `-v`, `--debug`, `--verbose` – enable debug logging for that adapter.
- `-h`, `--help` – show full usage/help from `argparse`.

### Musoni Example

```bash
cd /home/setup/infrafabric
python3 if.api/fintech/cbs/musoni/example_usage.py -d
```

Sets `IF_FINTECH_DEBUG_MUSONI=1` for the run and logs HTTP requests/responses
made by the Musoni adapter.

### Smile Identity Example

```bash
python3 if.api/fintech/kyc/smile-identity/example_usage.py --debug
```

Sets `IF_FINTECH_DEBUG_SMILE_IDENTITY=1`.

### TransUnion Example

```bash
python3 if.api/fintech/kyc/transunion/example_usage.py -v
```

Sets `IF_FINTECH_DEBUG_TRANSUNION=1`.

### Africa's Talking Example

```bash
python3 if.api/fintech/messaging/africas-talking/example_usage.py --verbose
```

Sets `IF_FINTECH_DEBUG_AFRICAS_TALKING=1`.

---

## Mobile Money Debug Flags

The mobile money adapters (M-Pesa, MTN MoMo, Airtel Money, Orange Money)
now call `ft_debug_log_request` / `ft_debug_log_response` around their HTTP
calls. You can enable per-adapter flags such as:

```bash
export IF_FINTECH_DEBUG_MPESA=1
export IF_FINTECH_DEBUG_MTN_MOMO=1
export IF_FINTECH_DEBUG_AIRTEL_MONEY=1
export IF_FINTECH_DEBUG_ORANGE_MONEY=1
```

Example invocations:

- M-Pesa:

```bash
python3 if.api/fintech/mobile-money/mpesa/examples.py -d
```

- Airtel Money:

```bash
python3 if.api/fintech/mobile-money/airtel-money/example_usage.py --debug
```

- Orange Money:

```bash
python3 if.api/fintech/mobile-money/orange-money/example_usage.py -v
```

- MTN MoMo:

```bash
python3 if.api/fintech/mobile-money/mtn-momo/example_usage.py --debug
```

This keeps fintech adapters aligned with the LLM debug tooling and makes it
much easier for Antoine's team to troubleshoot API integrations without
bespoke logging per provider.
