# LLM Integrations & Debugging

InfraFabric integrates multiple LLM providers under the `if.api/llm/` tree.
This page documents the available adapters and the shared debug utilities
you can enable when troubleshooting.

## LLM Adapters Overview

| Provider   | Adapter Path                     | Example Script                                      | Env Key              |
|-----------|-----------------------------------|-----------------------------------------------------|----------------------|
| Claude    | `if.api/llm/claude/`             | `if.api/llm/claude/test_claude_max_current.py`      | `CLAUDE_API_KEY`     |
| Gemini    | `if.api/llm/gemini/`             | `if.api/llm/gemini/gemini_librarian.py`             | `GEMINI_API_KEY`     |
| OpenAI    | `if.api/llm/openai/`             | `if.api/llm/openai/example_usage.py`                | `OPENAI_API_KEY`     |
| Mistral   | `if.api/llm/mistral/`            | `if.api/llm/mistral/example_usage.py`               | `MISTRAL_API_KEY`    |
| DeepSeek  | `if.api/llm/deepseek/`           | `if.api/llm/deepseek/example_usage.py`              | `DEEPSEEK_API_KEY`   |
| OpenRouter| `if.api/llm/openrouter/`         | `if.api/llm/openrouter/example_usage.py`            | `OPENROUTER_API_KEY` |
| OpenWebUI | `if.api/llm/openwebui/`          | CLI + tests under `if.api/llm/openwebui/`           | See OpenWebUI docs   |

All HTTP-based adapters (OpenAI, Mistral, DeepSeek, OpenRouter) share a
common debug utility module so you can get consistent request/response logs.

---

## Shared LLM Debug Utilities

**Module:** `llm_debug_utils.py` (project root)

Exports:

- `is_debug_enabled(provider: Optional[str]) -> bool`
- `debug_log_request(logger, provider, url, payload)`
- `debug_log_response(logger, provider, status_code, body_text)`

Each adapter calls these helpers around its HTTP requests, so you can enable
debug logging without changing application code.

### Environment Flags

Debug is controlled via environment variables:

- Global flag for all LLM adapters:

```bash
export IF_LLM_DEBUG=1
```

- Per-provider flags (override or complement the global flag):

```bash
export IF_LLM_DEBUG_OPENAI=1
export IF_LLM_DEBUG_MISTRAL=1
export IF_LLM_DEBUG_DEEPSEEK=1
export IF_LLM_DEBUG_OPENROUTER=1
```

When enabled, the adapter logs:
- Outgoing URL and JSON payload (truncated to a safe length).
- Incoming HTTP status code and response body preview.

Sensitive fields (API keys) are not logged; however, you should still avoid
enabling debug in production environments.

---

## CLI Usage: `-d/-v/--debug/--verbose`

Each HTTP-based LLM adapter ships with a small example script that can be
run directly. All of them support the same CLI flags:

- `-d`, `-v`, `--debug`, `--verbose` – enable debug logging for that provider.
- `-h`, `--help` – show full usage/help from `argparse`.

### OpenAI Example

```bash
cd /home/setup/infrafabric
python3 if.api/llm/openai/example_usage.py -d
```

This will:
- Set `IF_LLM_DEBUG_OPENAI=1` inside the script.
- Run a simple chat completion and log request/response details via
  `llm_debug_utils`.

### Mistral Example

```bash
python3 if.api/llm/mistral/example_usage.py --debug
```

Sets `IF_LLM_DEBUG_MISTRAL=1` for that run.

### DeepSeek Example

```bash
python3 if.api/llm/deepseek/example_usage.py -v
```

Sets `IF_LLM_DEBUG_DEEPSEEK=1`.

### OpenRouter Example

```bash
python3 if.api/llm/openrouter/example_usage.py --verbose
```

Sets `IF_LLM_DEBUG_OPENROUTER=1`.

---

## Pattern for Other Adapters

The same pattern (shared debug utilities + `-d/-v/--debug/--verbose` flags)
can be reused for any HTTP-based adapter, including:

- Future LLM providers added under `if.api/llm/`.
- Fintech integrations under `if.api/fintech/` (e.g. mobile money, KYC, CBS).

Recommended steps when extending:

1. Add calls to `debug_log_request` / `debug_log_response` around the central
   HTTP request function in the adapter (usually a `_request` or `_make_request`
   helper).
2. Add a small `example_usage.py` script with `argparse` that supports:
   - `-d`, `-v`, `--debug`, `--verbose`
   - `-h`, `--help`
3. Use provider-specific flags (e.g. `IF_LLM_DEBUG_PROVIDERNAME`) so you can
   enable debugging selectively.

Fintech adapters can follow the exact same approach with a dedicated
debug utility module (e.g. `fintech_debug_utils.py`) and matching env
flags (for example `IF_FINTECH_DEBUG_MPESA`, `IF_FINTECH_DEBUG_MTN_MOMO`, etc.).

### Secret Redaction via if.armour.secrets.detect

When debugging against real systems, you can enable automatic secret
redaction in LLM debug logs using the IF.yologuard engine exposed as
`infrafabric.core.armour.secrets.detect`:

- Global redaction flag (applies to all debug logs):

```bash
export IF_DEBUG_REDACT=1
```

- LLM‑wide redaction:

```bash
export IF_LLM_DEBUG_REDACT=1
```

- Provider‑specific redaction (for example OpenAI only):

```bash
export IF_LLM_DEBUG_REDACT_OPENAI=1
```

When these flags are set, `llm_debug_utils` runs payloads and response
snippets through `SecretRedactorV3` before logging, so API keys and other
secrets are scrubbed while still giving enough context for troubleshooting.
