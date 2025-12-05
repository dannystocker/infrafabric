# OpenRouter LLM Adapter

Thin HTTP adapter for the OpenRouter API, following the InfraFabric `if.api`
patterns and exposing a simple chat completions interface.

**Status:** Implementing  
**Default Endpoint:** `https://openrouter.ai/api/v1`  
**Env Key:** `OPENROUTER_API_KEY`

---

## Quick Start

```python
from openrouter_adapter import OpenRouterChatAdapter, ChatMessage

adapter = OpenRouterChatAdapter(
    api_key=None,  # falls back to OPENROUTER_API_KEY
    model="openrouter/auto",
    site_url="https://yourapp.example.com",
    app_name="InfraFabric Demo",
)

response = adapter.chat_completion(
    messages=[
        ChatMessage(role="user", content="Give me a concise InfraFabric pitch."),
    ],
)

print(response["choices"][0]["message"]["content"])
```

See `openrouter_adapter.py` for full details and options.

