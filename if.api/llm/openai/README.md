# OpenAI LLM Adapter

Thin Python adapter around the OpenAI Chat Completions HTTP API, structured
to fit the InfraFabric `if.api` pattern.

**Status:** Implementing  
**Default Endpoint:** `https://api.openai.com/v1`  
**Env Key:** `OPENAI_API_KEY`

---

## Quick Start

```python
from openai_adapter import OpenAIChatAdapter, ChatMessage

adapter = OpenAIChatAdapter(
    api_key=None,  # falls back to OPENAI_API_KEY
    model="gpt-4.1-mini",
)

response = adapter.chat_completion(
    messages=[
        ChatMessage(role="user", content="Explain InfraFabric in one sentence."),
    ],
    temperature=0.7,
)

print(response["choices"][0]["message"]["content"])
```

See `openai_adapter.py` for full details and options.

