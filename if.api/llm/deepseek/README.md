# DeepSeek LLM Adapter

Thin HTTP adapter for the DeepSeek chat completions API, aligned with the
InfraFabric `if.api` patterns.

**Status:** Implementing  
**Default Endpoint:** `https://api.deepseek.com/v1`  
**Env Key:** `DEEPSEEK_API_KEY`

---

## Quick Start

```python
from deepseek_adapter import DeepSeekChatAdapter, ChatMessage

adapter = DeepSeekChatAdapter(
    api_key=None,  # falls back to DEEPSEEK_API_KEY
    model="deepseek-chat",
)

response = adapter.chat_completion(
    messages=[
        ChatMessage(role="user", content="Explain InfraFabric in two sentences."),
    ],
)

print(response["choices"][0]["message"]["content"])
```

See `deepseek_adapter.py` for full details and options.

