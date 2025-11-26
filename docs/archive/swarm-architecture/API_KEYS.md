# API KEYS REFERENCE
**For Instance #9 Gemini Librarian**

---

## 🔑 Gemini API Keys

### Shard 1: danny.stocker@gmail.com (ACTIVE)
```
AIzaSyDSnIE3eKXoUmeydbUn9wdbwBxWPlJJgn4
```

**Tier:** Free
**Limits:**
- 15 requests/minute
- 1,500 requests/day
- 1M tokens/minute

**Status:** ✅ Working (validated 2025-11-21)
**Used in:** `gemini_librarian.py`, `test_gemini_flash.sh`

---

### Shard 2: dstocker.ca@gmail.com (ACTIVE)
```
AIzaSyDzLJU-9-nEwUsj5wgmYyOzT07uNU4KUEY
```

**Tier:** Free
**Limits:**
- 15 requests/minute
- 1,500 requests/day
- 1M tokens/minute

**Status:** ✅ Available
**Combined Capacity:** 3,000 requests/day (2 free tier accounts)

**Get keys here:** https://aistudio.google.com/app/apikey

---

### Shard 3: dstocker.ca@gmail.com (ACTIVE)
```
AIzaSyDzLJU-9-nEwUsj5wgmYyOzT07uNU4KUEY
```

**Tier:** Free
**Limits:**
- 15 requests/minute
- 1,500 requests/day
- 1M tokens/minute

**Status:** ✅ Available

---

### Shard 4: ds@etre.net (ACTIVE - InfraFabric)
```
AIzaSyBU8EeW8n9tiaw_NR7PcbBhH7cFoC8LWnk
```

**Tier:** Free
**Limits:**
- 15 requests/minute
- 1,500 requests/day
- 1M tokens/minute

**Status:** ✅ Available
**Combined Capacity (4 shards):** 6,000 requests/day

---

### Shard 5: ds@digital-lab.ca
```
AIzaSyB3yQZSAlgN_36NwOQMp7rf0f1f75pPmfk
```

**Tier:** Free
**Limits:**
- 15 requests/minute
- 1,500 requests/day
- 1M tokens/minute

**Status:** ⏳ Quota exhausted during initial testing (2025-11-21)
**Note:** Quota resets daily, available tomorrow
**Combined Capacity (all 5 shards):** 7,500 requests/day

---

## 🚀 MULTI-SHARD STRATEGY

With **4-5 free tier accounts**, you can **4-5× your capacity**:

**Combined Limits (4 active shards):**
- **60 requests/minute** (15 × 4)
- **6,000 requests/day** (1,500 × 4)
- **4M tokens/minute** (1M × 4)

### Load Balancing Pattern

```python
# Round-robin between 4 active shards
GEMINI_KEYS = [
    "AIzaSyDSnIE3eKXoUmeydbUn9wdbwBxWPlJJgn4",  # danny.stocker@gmail.com
    "AIzaSyDzLJU-9-nEwUsj5wgmYyOzT07uNU4KUEY",  # dstocker.ca@gmail.com
    "AIzaSyBU8EeW8n9tiaw_NR7PcbBhH7cFoC8LWnk",  # ds@etre.net (InfraFabric)
    # "AIzaSyB3yQZSAlgN_36NwOQMp7rf0f1f75pPmfk",  # ds@digital-lab.ca (quota reset tomorrow)
]

class MultiShardLibrarian:
    def __init__(self):
        self.current_shard = 0
        self.librarians = [
            GeminiLibrarian(api_key=key) for key in GEMINI_KEYS
        ]

    def query(self, question):
        """Round-robin across shards"""
        librarian = self.librarians[self.current_shard]
        self.current_shard = (self.current_shard + 1) % len(self.librarians)

        try:
            return librarian.query_archive(question)
        except QuotaExceededError:
            # Try next shard
            return self.librarians[self.current_shard].query_archive(question)
```

**Cost Savings:**
- Free tier × 4 shards = **$0/month** for 6,000 queries/day
- vs Haiku: $3,623/month for same volume
- **Savings: $43,476/year** 🎉

---

## 🔄 How to Switch Keys

### Method 1: Environment Variable (Recommended)
```bash
export GEMINI_API_KEY="AIzaSyDSnIE3eKXoUmeydbUn9wdbwBxWPlJJgn4"
python gemini_librarian.py --mode query --question "..."
```

### Method 2: .env File
```bash
# Create .env file
echo 'GEMINI_API_KEY=AIzaSyDSnIE3eKXoUmeydbUn9wdbwBxWPlJJgn4' > .env

# Load in Python
from dotenv import load_dotenv
load_dotenv()
```

### Method 3: Command Line Argument
```bash
python gemini_librarian.py --api-key "AIzaSyD..." --mode query
```

---

## 📊 Key Management Best Practices

### Security
- ❌ Never commit keys to git
- ✅ Use `.env` files (add to `.gitignore`)
- ✅ Use environment variables in production
- ✅ Rotate keys periodically

### Monitoring
- Track daily usage (1,500 query limit)
- Monitor rate limits (15 RPM)
- Set up alerts at 80% quota
- Log quota exhaustion events

### Upgrading to Paid Tier
1. Go to: https://console.cloud.google.com/
2. Enable billing on your project
3. Limits automatically increase:
   - 15 RPM → 2,000 RPM
   - 1,500 RPD → Unlimited
4. Start paying per-token (see FREE_TIER_GUIDE.md)

---

## 🔐 Other API Keys (For Reference)

### OpenRouter
```
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
```
**Status:** REVOKED (exposed in GitHub)

### DeepSeek
```
sk-c2b06f3ae3c442de82f4e529bcce71ed
```
**Status:** Active (from CLAUDE.md)

---

---

## 🔷 DeepSeek API Keys

### DeepSeek V3 (Redis Shard)
```
Email: dstocker.ca@gmail.com
API Key: sk-bca3dd2e420f428495f65915701b0244
Purpose: Redis swarm worker shard
```

**Model:** DeepSeek V3
**Pricing:**
- Input: $0.60 /M tokens
- Output: $1.70 /M tokens
- Batch Input: $0.30 /M tokens
- Batch Output: $0.85 /M tokens

**vs Gemini 2.5 Flash Lite:**
- Input: 6× more expensive ($0.60 vs $0.10)
- Output: 4.25× more expensive ($1.70 vs $0.40)

**Use case:** Specialized tasks where DeepSeek excels, or as fallback when all Gemini shards exhausted.

---

## 📝 Notes

- All keys documented in `/home/setup/.claude/CLAUDE.md`
- **Primary Archive:** 4-5× Gemini shards (free tier, $0/month)
- **Fallback 1:** DeepSeek V3 (paid, cheaper than Claude/GPT)
- **Fallback 2:** Claude Haiku (Pro Max subscription)
- Upgrade decision tree in `FREE_TIER_GUIDE.md`
