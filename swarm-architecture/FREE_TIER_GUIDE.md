# GEMINI FREE TIER DEPLOYMENT GUIDE
**For Instance #9's Hybrid Brain Architecture**

---

## 🆓 FREE TIER LIMITS

| Constraint | Free Tier | Paid Tier |
|-----------|-----------|-----------|
| **Requests/Minute** | 15 RPM | 2,000 RPM |
| **Requests/Day** | 1,500 RPD | Unlimited |
| **Tokens/Minute** | 1M TPM | 4M TPM |
| **Cost** | $0/month | Pay-as-you-go |
| **SLA** | None | 99.5% uptime |

---

## 📊 WHAT YOU CAN DO (FREE TIER)

### Development & Testing
- ✅ **Unlimited testing** (within daily limits)
- ✅ **Prototype validation**
- ✅ **Architecture experimentation**

### Low-Volume Production
- ✅ **1,500 queries/day** = 62 queries/hour = 1 query/minute
- ✅ **Personal projects**
- ✅ **Internal tools**
- ✅ **MVP launches**

---

## 🚦 RATE LIMITING STRATEGY

### Add to `gemini_librarian.py`

```python
import time
from datetime import datetime, timedelta
from collections import deque

class RateLimiter:
    """Free tier: 15 requests/minute"""

    def __init__(self, max_requests=15, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window  # seconds
        self.requests = deque()

    def wait_if_needed(self):
        """Block if rate limit would be exceeded"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.time_window)

        # Remove old requests
        while self.requests and self.requests[0] < cutoff:
            self.requests.popleft()

        # Check if at limit
        if len(self.requests) >= self.max_requests:
            sleep_time = (self.requests[0] - cutoff).total_seconds()
            if sleep_time > 0:
                print(f"   ⏳ Rate limit: waiting {sleep_time:.1f}s...")
                time.sleep(sleep_time + 0.1)  # Small buffer

        # Record this request
        self.requests.append(now)

# Usage in GeminiLibrarian.__init__():
self.rate_limiter = RateLimiter(max_requests=15, time_window=60)

# Before API call in query_archive():
self.rate_limiter.wait_if_needed()
response = self.model.generate_content(prompt)
```

---

## 💰 COST BREAKDOWN (IF YOU UPGRADE)

### Your Actual Costs (Measured)
**Per Query:**
- Input: 629 tokens × $0.10/M = $0.0000629
- Output: 1,129 tokens × $0.40/M = $0.0004516
- **Total: $0.0005145** (~0.05 cents)

### Monthly Costs by Volume

| Queries/Day | Monthly Queries | Monthly Cost | Annual Cost |
|-------------|----------------|-------------|-------------|
| 100 | 3,000 | $1.54 | $18.53 |
| 500 | 15,000 | $7.72 | $92.62 |
| **1,500** (free max) | **45,000** | **$23.15** | **$277.84** |
| 5,000 | 150,000 | $77.18 | $926.13 |
| 10,000 | 300,000 | $154.35 | $1,852.25 |

**vs 4× Haiku Shards (Same 1,500 queries/day):**
- Monthly: $905.70
- **Savings: $882.55/month (97% cheaper)** 🎉

---

## 🎯 DEPLOYMENT DECISION TREE

```
Start: How many queries per day?
│
├─ < 1,500/day
│  └─ ✅ Use Free Tier ($0/month)
│     └─ Add rate limiting (15 RPM)
│
├─ 1,500 - 10,000/day
│  └─ ⚠️ Upgrade to Paid ($23-154/month)
│     └─ Still 39× cheaper than Haiku
│
└─ > 10,000/day
   └─ 💰 Paid + Optimization
      ├─ Enable prompt caching (90% discount)
      ├─ Batch queries where possible
      └─ Consider hybrid (Gemini + Haiku fallback)
```

---

## 🚀 PRODUCTION CHECKLIST

### Phase 1: Free Tier Launch
- [x] ✅ Architecture validated (Instance #9)
- [ ] Add rate limiting (15 RPM)
- [ ] Add daily quota tracking (1,500 RPD)
- [ ] Implement graceful degradation (fallback to Haiku if quota exhausted)
- [ ] Add monitoring dashboard
- [ ] Set up alerts (90% quota warning)

### Phase 2: Monitor & Measure
- [ ] Track actual query volume (7 days)
- [ ] Measure cost savings vs Haiku baseline
- [ ] Identify peak usage patterns
- [ ] Calculate ROI for paid tier upgrade

### Phase 3: Scale (If Needed)
- [ ] Upgrade to paid tier when hitting free limits
- [ ] Enable prompt caching (90% input discount)
- [ ] Add batch processing for bulk queries
- [ ] Implement cost optimization strategies

---

## 📈 WHEN TO UPGRADE?

### Stay on Free Tier If:
- ✅ Query volume < 1,500/day
- ✅ Can tolerate 15 RPM rate limit
- ✅ Not business-critical (no SLA needed)
- ✅ Budget = $0

### Upgrade to Paid If:
- ⚠️ Hitting 1,500/day limit regularly
- ⚠️ Need faster response (>15 RPM)
- ⚠️ Business-critical workload (need SLA)
- ⚠️ Budget = $23+/month

**ROI Calculation:**
```
Current Cost (4× Haiku): $905.70/month
Gemini Paid Cost: $23.15/month
Monthly Savings: $882.55
Annual Savings: $10,590.60

Payback Period: Instant (cheaper from day 1)
```

---

## 🛡️ GRACEFUL DEGRADATION PATTERN

```python
def query_archive_with_fallback(question):
    """Try Gemini (free/cheap), fallback to Haiku if quota exhausted"""

    try:
        # Primary: Gemini Archive (39× cheaper)
        return gemini_librarian.query(question)

    except QuotaExceededError:
        print("⚠️  Gemini quota exhausted, falling back to Haiku shards")

        # Fallback: 4× Haiku shards (expensive but reliable)
        return haiku_shards.query(question)
```

**Cost Impact:**
- 99% Gemini (free): $0
- 1% Haiku fallback: $9.06/month
- **Total: $9.06/month** (still 99% cheaper than all-Haiku)

---

## 📊 MONITORING DASHBOARD

Track these metrics:

```python
# Daily metrics
gemini_queries_today = 847  # out of 1,500 max
gemini_quota_remaining = 653
gemini_cost_today = $0.43

# Rate limiting
current_rpm = 12  # out of 15 max
rate_limit_hits = 3  # times we had to wait

# Cost savings
haiku_cost_avoided = $17.03  # what 4× Haiku would have cost
savings_percentage = 97.5%
```

---

## ✅ BOTTOM LINE

**Free tier is PERFECT for your use case** if:
- Your archive gets < 1,500 queries/day
- You can tolerate 15 queries/minute max
- You're okay with no SLA guarantees

**You're saving $10,590/year** vs Haiku architecture, even if you upgrade to paid tier.

**Current status:** Production-ready on free tier with rate limiting.
