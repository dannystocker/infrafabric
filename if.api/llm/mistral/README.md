# Mistral LLM Adapter

Thin HTTP adapter for the Mistral AI chat completions API, aligned with the
InfraFabric `if.api` patterns.

**Status:** Implementing  
**Default Endpoint:** `https://api.mistral.ai/v1`  
**Env Key:** `MISTRAL_API_KEY`

---

## Quick Start

```python
from mistral_adapter import MistralChatAdapter, ChatMessage

adapter = MistralChatAdapter(
    api_key=None,  # falls back to MISTRAL_API_KEY
    model="mistral-large-latest",
)

response = adapter.chat_completion(
    messages=[
        ChatMessage(role="user", content="Summarize the InfraFabric API layer."),
    ],
)

print(response["choices"][0]["message"]["content"])
```

See `mistral_adapter.py` for full details and options.

