# Airtel Money Adapter - Quick Start Guide

Get started with Airtel Money integration in 5 minutes.

## Step 1: Set Environment Variables

Create a `.env` file:

```bash
# Required
AIRTEL_CLIENT_ID=your-client-id-here
AIRTEL_CLIENT_SECRET=your-client-secret-here

# Optional (with defaults)
AIRTEL_COUNTRY=KE
AIRTEL_ENVIRONMENT=production
AIRTEL_PIN=your-pin-for-disbursements
AIRTEL_CALLBACK_URL=https://yourdomain.com/callbacks/airtel
```

## Step 2: Install Dependencies

```bash
pip install requests
```

## Step 3: Basic Usage

### Initialize the Adapter

```python
from airtel_money_adapter import AirtelMoneyAdapter, CountryCode
import os

adapter = AirtelMoneyAdapter(
    client_id=os.getenv("AIRTEL_CLIENT_ID"),
    client_secret=os.getenv("AIRTEL_CLIENT_SECRET"),
    country=CountryCode.KENYA,
    environment="production",  # or "sandbox" for testing
)
```

### Check Balance

```python
balance = adapter.get_balance()
print(f"Balance: {balance['balance']} {balance['currency']}")
```

### Send Money (Disbursement)

```python
result = adapter.transfer(
    amount=1000.00,
    msisdn="254712345678",
    reference="DISB-001",
    description="Loan disbursement",
    pin="1234"
)

print(f"Transaction ID: {result['transaction_id']}")
print(f"Status: {result['status']}")
```

### Request Payment (Collection)

```python
result = adapter.ussd_push(
    amount=500.00,
    msisdn="254712345678",
    reference="COLL-001",
    description="Loan repayment"
)

print(f"Transaction ID: {result['transaction_id']}")
print("Customer will receive USSD prompt to approve payment")
```

### Verify Customer (KYC)

```python
kyc = adapter.kyc_inquiry("254712345678")

if kyc.is_verified:
    print(f"Customer verified: {kyc.full_name}")
    print(f"ID Number: {kyc.id_number}")
else:
    print("Customer not verified")
```

## Step 4: Check Transaction Status

```python
# For collections
status = adapter.get_collection_status("transaction-id")
print(f"Status: {status['status']}")

# For disbursements
status = adapter.get_disbursement_status("transaction-id")
print(f"Status: {status['status']}")
```

## Step 5: Handle Callbacks (Optional)

```python
from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/callbacks/airtel', methods=['POST'])
def airtel_callback():
    # Verify signature
    signature = request.headers.get('X-Signature')
    body = request.get_data(as_text=True)

    if not adapter.verify_callback_signature(signature, body):
        return {'error': 'Invalid signature'}, 401

    # Process callback
    callback_data = json.loads(body)
    adapter.handle_callback(callback_data)

    return {'success': True}, 200

if __name__ == '__main__':
    app.run(port=5000)
```

## Complete Example: Microfinance Workflow

```python
from airtel_money_adapter import AirtelMoneyAdapter, CountryCode
import os

# Initialize
adapter = AirtelMoneyAdapter(
    client_id=os.getenv("AIRTEL_CLIENT_ID"),
    client_secret=os.getenv("AIRTEL_CLIENT_SECRET"),
    country=CountryCode.KENYA,
    pin=os.getenv("AIRTEL_PIN"),
)

# 1. Verify customer
customer_phone = "254712345678"
kyc = adapter.kyc_inquiry(customer_phone)

if not kyc.is_verified:
    print("Customer not verified - cannot proceed")
    exit(1)

print(f"Customer verified: {kyc.full_name}")

# 2. Check balance before disbursement
balance = adapter.get_balance()
loan_amount = 5000.00

if balance['balance'] < loan_amount:
    print(f"Insufficient balance: {balance['balance']}")
    exit(1)

# 3. Disburse loan
print(f"Disbursing {loan_amount} to {customer_phone}...")
result = adapter.transfer(
    amount=loan_amount,
    msisdn=customer_phone,
    reference="LOAN-12345",
    description=f"Loan to {kyc.full_name}",
)

print(f"✓ Loan disbursed!")
print(f"  Transaction ID: {result['transaction_id']}")
print(f"  Status: {result['status']}")

# 4. Check status
status = adapter.get_disbursement_status(result['transaction_id'])
print(f"  Final Status: {status['status']}")

# 5. Close adapter
adapter.close()
```

## Error Handling

```python
from airtel_money_adapter import (
    ValidationError,
    AuthenticationError,
    APIError,
    InsufficientBalanceError,
)

try:
    result = adapter.transfer(
        amount=5000.00,
        msisdn="254712345678",
        reference="LOAN-001",
        description="Loan"
    )
except ValidationError as e:
    print(f"Invalid input: {e}")
except AuthenticationError as e:
    print(f"Auth failed: {e}")
except InsufficientBalanceError as e:
    print(f"Not enough funds: {e}")
except APIError as e:
    print(f"API error: {e}")
```

## Using Context Manager (Recommended)

```python
from airtel_money_adapter import AirtelMoneyAdapter, CountryCode
import os

with AirtelMoneyAdapter(
    client_id=os.getenv("AIRTEL_CLIENT_ID"),
    client_secret=os.getenv("AIRTEL_CLIENT_SECRET"),
    country=CountryCode.KENYA,
) as adapter:
    # All operations here
    balance = adapter.get_balance()
    print(f"Balance: {balance['balance']}")

# Adapter automatically closed
```

## Supported Countries

```python
from config import list_supported_countries

for country in list_supported_countries():
    print(f"{country.name} ({country.code}): {country.currency}")
```

Output:
```
Kenya (KE): KES
Uganda (UG): UGX
Tanzania (TZ): TZS
Rwanda (RW): RWF
Zambia (ZM): ZMW
Malawi (MW): MWK
Nigeria (NG): NGN
DRC (CD): CDF
Madagascar (MG): MGA
Seychelles (SC): SCR
Chad (TD): XAF
Gabon (GA): XAF
Niger (NE): XOF
Congo-Brazzaville (CG): XAF
```

## Phone Number Format

All phone numbers must be in international format (E.164):

```python
# Correct formats:
"254712345678"  # Kenya
"+254712345678"  # Also accepted
"0712345678"  # Automatically converted to 254712345678 (Kenya)

# Incorrect:
"712345678"  # Missing country code
```

## Testing with Sandbox

```python
adapter = AirtelMoneyAdapter(
    client_id="sandbox-client-id",
    client_secret="sandbox-client-secret",
    environment="sandbox",  # Use sandbox for testing
    country=CountryCode.KENYA,
)

# All API calls will go to sandbox environment
```

## Next Steps

1. Read full documentation in [README.md](README.md)
2. Explore examples in [example_usage.py](example_usage.py)
3. Review configuration options in [config.py](config.py)
4. Test in sandbox environment
5. Deploy to production

## Get Help

- Check [README.md](README.md) for detailed documentation
- Review error logs with proper logging:
  ```python
  import logging
  logging.basicConfig(level=logging.DEBUG)
  ```
- Contact Airtel Money support for API issues

## Common Issues

**Authentication fails:**
- Verify client ID and secret are correct
- Check environment (sandbox vs production)
- Ensure credentials match environment

**Phone number invalid:**
- Use international format: `254712345678`
- Include country code
- Remove spaces and special characters

**Insufficient balance:**
- Check balance with `get_balance()`
- Top up account
- Verify correct account

**Transaction fails:**
- Check transaction limits for country
- Verify customer account is active
- Review error message in response

---

Ready to integrate Airtel Money! Start with sandbox and move to production when ready.
