# M-Pesa Adapter - Quick Start Guide

## 1. Setup (5 minutes)

### Get Your Credentials

1. Go to https://developer.safaricom.co.ke/
2. Sign up and create an app
3. Copy **Consumer Key** and **Consumer Secret**
4. Get your **Business Shortcode** from M-Pesa
5. Get your **Online Passkey** from M-Pesa Business settings

### Set Environment Variables

```bash
export MPESA_CONSUMER_KEY="your_consumer_key"
export MPESA_CONSUMER_SECRET="your_consumer_secret"
export MPESA_BUSINESS_SHORTCODE="123456"
export MPESA_PASSKEY="your_online_passkey"
export MPESA_ENVIRONMENT="sandbox"  # Use "production" for live
```

### Install Package

```bash
pip install requests
```

## 2. Basic Usage (Copy-Paste Ready)

### Payment Collection (STK Push)

```python
from if.api.fintech.mobile_money.mpesa import create_mpesa_adapter

# Initialize
adapter = create_mpesa_adapter(environment="sandbox")

# Ask customer to pay
result = adapter.initiate_stk_push(
    phone_number="254712345678",      # Must be in 254... format
    amount=100.00,                     # Amount in KES
    account_reference="ORDER_123"      # Your reference ID
)

print(f"Prompt sent! Checkout ID: {result['CheckoutRequestID']}")

# Check status after customer enters PIN
import time
time.sleep(5)

status = adapter.query_stk_push_status(result['CheckoutRequestID'])
print(f"Status: {status['ResultDescription']}")

adapter.close()
```

### Send Money to Customer (B2C)

```python
from if.api.fintech.mobile_money.mpesa import create_mpesa_adapter

adapter = create_mpesa_adapter(environment="sandbox")

# Send salary
result = adapter.b2c_payment(
    phone_number="254712345678",
    amount=5000.00,
    command_id="SalaryPayment",
    remarks="December Salary"
)

print(f"Payment initiated: {result['ConversationID']}")
adapter.close()
```

### Check Account Balance

```python
from if.api.fintech.mobile_money.mpesa import create_mpesa_adapter

adapter = create_mpesa_adapter()
balance = adapter.get_account_balance()
print(f"Balance query sent: {balance['ConversationID']}")
adapter.close()
```

### Check Transaction Status

```python
from if.api.fintech.mobile_money.mpesa import create_mpesa_adapter

adapter = create_mpesa_adapter()

# Get status of any M-Pesa transaction
status = adapter.query_transaction_status("LHG31AA5695")
print(f"Status: {status['ResultDescription']}")

adapter.close()
```

## 3. Phone Number Format

| Format | Result |
|--------|--------|
| `254712345678` | ✓ Correct |
| `0712345678` | Auto-converted to 254712345678 |
| `+254712345678` | Auto-converted to 254712345678 |

```python
from if.api.fintech.mobile_money.mpesa import PhoneNumberValidator

# Validate and format
phone = PhoneNumberValidator.clean("0712345678")  # Returns "254712345678"
```

## 4. Error Handling

```python
from if.api.fintech.mobile_money.mpesa import (
    create_mpesa_adapter,
    MpesaAuthException,
    MpesaAPIException,
    MpesaException
)

adapter = create_mpesa_adapter()

try:
    result = adapter.initiate_stk_push(
        phone_number="254712345678",
        amount=100.0,
        account_reference="ORDER_001"
    )
except MpesaAuthException as e:
    print(f"Auth failed: {e}")
except MpesaAPIException as e:
    print(f"API error: {e}")
except MpesaException as e:
    print(f"M-Pesa error: {e}")
finally:
    adapter.close()
```

## 5. IF.bus Event Tracking

```python
from if.api.fintech.mobile_money.mpesa import (
    MpesaAdapter,
    Environment,
    MpesaEventEmitter
)

# Create custom event handler
class EventLogger(MpesaEventEmitter):
    def emit(self, event_name: str, data: dict):
        print(f"[EVENT] {event_name}")
        print(f"[DATA] {data}")
        # Send to IF.bus, log to DB, etc.

# Use with adapter
adapter = MpesaAdapter(
    consumer_key="key",
    consumer_secret="secret",
    business_shortcode="123456",
    passkey="passkey",
    environment=Environment.SANDBOX,
    event_emitter=EventLogger()
)

# Events emitted automatically:
# - mpesa.auth.token_acquired
# - mpesa.stk_push.initiated
# - mpesa.stk_push.success or mpesa.stk_push.failed
# - mpesa.b2c.initiated
# - mpesa.b2c.success or mpesa.b2c.failed
# - mpesa.error.occurred
```

## 6. Input Validation

```python
from if.api.fintech.mobile_money.mpesa import (
    PhoneNumberValidator,
    AmountValidator
)

# Validate phone
try:
    phone = PhoneNumberValidator.clean("0712345678")
    print(f"Valid: {phone}")
except ValueError as e:
    print(f"Invalid: {e}")

# Validate amount
try:
    AmountValidator.validate_strict(100.0)  # OK
    AmountValidator.validate_strict(0.5)    # Raises ValueError (too small)
except ValueError as e:
    print(f"Invalid amount: {e}")

# Amount limits: 1 KES - 150,000 KES
```

## 7. Testing

### Create Mock Adapter

```python
from if.api.fintech.mobile_money.mpesa.test_helpers import (
    MpesaAdapterTestHelper,
    MockMpesaResponses
)

# Create mock adapter
adapter = MpesaAdapterTestHelper.create_mock_adapter()

# Mock STK Push response
MpesaAdapterTestHelper.mock_stk_push_response(adapter, success=True)

# Use normally - returns mocked response
result = adapter.initiate_stk_push(
    phone_number="254712345678",
    amount=100.0,
    account_reference="TEST"
)

# Verify events
events = adapter.event_emitter.get_events()
print(f"Events emitted: {len(events)}")
```

## 8. Configuration Methods

### Method 1: Environment Variables

```python
from if.api.fintech.mobile_money.mpesa import create_mpesa_adapter

# Reads: MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET, etc.
adapter = create_mpesa_adapter(environment="sandbox")
```

### Method 2: Direct Parameters

```python
from if.api.fintech.mobile_money.mpesa import MpesaAdapter, Environment

adapter = MpesaAdapter(
    consumer_key="key",
    consumer_secret="secret",
    business_shortcode="123456",
    passkey="passkey",
    environment=Environment.SANDBOX
)
```

### Method 3: Configuration Class

```python
from if.api.fintech.mobile_money.mpesa import MpesaConfig

config = MpesaConfig.from_env()
config.validate()

adapter = MpesaAdapter(
    consumer_key=config.consumer_key,
    consumer_secret=config.consumer_secret,
    business_shortcode=config.business_shortcode,
    passkey=config.passkey,
    environment=config.environment
)
```

## 9. Timeout & Retry Configuration

```python
from if.api.fintech.mobile_money.mpesa import MpesaAdapter, Environment

adapter = MpesaAdapter(
    consumer_key="key",
    consumer_secret="secret",
    business_shortcode="123456",
    passkey="passkey",
    environment=Environment.SANDBOX,
    timeout=60,        # Increase timeout to 60 seconds
    max_retries=5      # Retry up to 5 times
)
```

## 10. Common Status Codes

```python
from if.api.fintech.mobile_money.mpesa import ResultCodes

# Result code meanings
ResultCodes.SUCCESS                # "0"
ResultCodes.INSUFFICIENT_FUNDS     # "1"
ResultCodes.LESS_AMOUNT            # "2"
ResultCodes.MORE_AMOUNT            # "3"
ResultCodes.EXEC_TIMEOUT           # "4"
ResultCodes.INTERNAL_ERROR         # "5"

# Get description
desc = ResultCodes.get_description("0")  # "Success"
```

## 11. Sandbox Test Data

**Test Phone Numbers**:
- 254712345678
- 254708374149
- 254706092517

**Test Shortcode**: 174379
**Test Passkey**: bfb279f9aa9bdbcf158e97dd1a503b6055c2f8e3c36a6e0c

## 12. Production Checklist

Before going live:

- [ ] Switch `MPESA_ENVIRONMENT` to "production"
- [ ] Update credentials to production values
- [ ] Implement certificate-based security credential encryption
- [ ] Configure proper callback URLs
- [ ] Add comprehensive error logging
- [ ] Implement webhook signature validation
- [ ] Test end-to-end with real M-Pesa account
- [ ] Review Safaricom security guidelines
- [ ] Set up monitoring and alerting
- [ ] Load test with expected transaction volume

## 13. Troubleshooting

### 401 Unauthorized

```
Problem: "Client authentication failed"
Solution: Check MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET are correct
```

### Invalid Shortcode

```
Problem: "Invalid merchant shortcode"
Solution: Verify shortcode in Daraja app settings
```

### Invalid Phone Number

```python
# Wrong
phone = "0712345678"  # Local format

# Right
phone = PhoneNumberValidator.clean("0712345678")  # Auto-converts
```

### Amount Out of Range

```python
# Wrong
amount = 0.5  # Too small (min: 1 KES)
amount = 200000  # Too large (max: 150,000 KES)

# Right
amount = 100.0  # Between 1 and 150,000
```

## 14. Full Reference

For complete documentation, see:
- `README.md` - Comprehensive guide
- `examples.py` - Code examples
- `IMPLEMENTATION_SUMMARY.md` - Technical details

## 15. Get Help

1. Check `examples.py` for your use case
2. Review error logs (check adapter logging)
3. Test in sandbox first
4. Visit https://developer.safaricom.co.ke/ for API docs
5. Check Safaricom Daraja support forum

---

**Quick Links**:
- Daraja Portal: https://developer.safaricom.co.ke/
- API Documentation: https://developer.safaricom.co.ke/Documentation
- Integration Guide: https://developer.safaricom.co.ke/docs
