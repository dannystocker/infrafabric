# Airtel Money Africa API Adapter

Production-ready Python adapter for Airtel Money APIs, providing seamless integration with Airtel's mobile financial services across 14 African countries.

## Features

- **Collections API**: USSD Push payment collection from subscribers
- **Disbursements API**: Money transfers to subscribers' mobile wallets
- **Account API**: Balance inquiries and account management
- **KYC API**: Customer verification and identity validation
- **Refund API**: Transaction refund capabilities
- **OAuth2 Authentication**: Client credentials flow with automatic token caching
- **Transaction Status Monitoring**: Real-time status checks and callbacks
- **IF.bus Integration**: Full event emission for transaction lifecycle
- **Multi-country Support**: 14 African countries with localized configurations
- **Type Hints & Docstrings**: Full type safety and comprehensive documentation
- **Error Handling**: Robust exception handling with custom exceptions
- **Retry Logic**: Automatic retry with exponential backoff
- **Sandbox & Production**: Support for both environments

## Supported Countries

| Country | Code | Currency | Phone Prefix |
|---------|------|----------|--------------|
| Kenya | KE | KES | +254 |
| Uganda | UG | UGX | +256 |
| Tanzania | TZ | TZS | +255 |
| Rwanda | RW | RWF | +250 |
| Zambia | ZM | ZMW | +260 |
| Malawi | MW | MWK | +265 |
| Nigeria | NG | NGN | +234 |
| DRC | CD | CDF | +243 |
| Madagascar | MG | MGA | +261 |
| Seychelles | SC | SCR | +248 |
| Chad | TD | XAF | +235 |
| Gabon | GA | XAF | +241 |
| Niger | NE | XOF | +227 |
| Congo-Brazzaville | CG | XAF | +242 |

## Installation

### Requirements

- Python 3.8+
- `requests` library

### Setup

```bash
pip install requests
```

## Configuration

### Environment Variables

Create `.env` file in your application:

```env
# Airtel Money Configuration
AIRTEL_CLIENT_ID=your-client-id
AIRTEL_CLIENT_SECRET=your-client-secret
AIRTEL_COUNTRY=KE  # Country code (KE, UG, TZ, etc.)
AIRTEL_ENVIRONMENT=production  # or "sandbox"
AIRTEL_PIN=your-pin  # Optional, for disbursements
AIRTEL_CALLBACK_URL=https://your-domain.com/callbacks/airtel-money
AIRTEL_TIMEOUT=30  # Request timeout in seconds
AIRTEL_MAX_RETRIES=3  # Maximum retry attempts
```

### Initialize Adapter

```python
import os
from airtel_money_adapter import AirtelMoneyAdapter, CountryCode

adapter = AirtelMoneyAdapter(
    client_id=os.getenv("AIRTEL_CLIENT_ID"),
    client_secret=os.getenv("AIRTEL_CLIENT_SECRET"),
    country=CountryCode.KENYA,
    environment=os.getenv("AIRTEL_ENVIRONMENT", "sandbox"),
    pin=os.getenv("AIRTEL_PIN"),
    callback_url=os.getenv("AIRTEL_CALLBACK_URL"),
)
```

### Using Configuration Module

```python
from config import AirtelMoneyConfig

# Load from environment variables
config = AirtelMoneyConfig.from_env()

# Initialize adapter with config
adapter = AirtelMoneyAdapter(
    client_id=config.client_id,
    client_secret=config.client_secret,
    country=CountryCode[config.country],
    environment=config.environment,
    pin=config.pin,
)
```

## Usage Examples

### Collections API (USSD Push)

Request payment from a subscriber:

```python
# Initiate USSD Push payment
result = adapter.ussd_push(
    amount=1000.00,
    msisdn="254712345678",  # International format
    reference="ORDER-12345",
    description="Payment for Order #12345"
)

print(f"Transaction ID: {result['transaction_id']}")
print(f"Status: {result['status']}")  # PENDING

# Check payment status
status = adapter.get_collection_status(result['transaction_id'])
print(f"Current status: {status['status']}")  # SUCCESS, FAILED, PENDING

if status['status'] == 'FAILED':
    print(f"Failure reason: {status['status_message']}")
```

### Disbursements API (Money Transfer)

Send money to a subscriber:

```python
# Transfer money
result = adapter.transfer(
    amount=5000.00,
    msisdn="254712345678",
    reference="LOAN-DISB-001",
    description="Loan disbursement",
    pin="1234"  # Optional if set in initialization
)

print(f"Transfer ID: {result['transaction_id']}")
print(f"Status: {result['status']}")  # SUCCESS or PENDING

# Check transfer status
status = adapter.get_disbursement_status(result['transaction_id'])
print(f"Transfer status: {status['status']}")
```

### Account API

Check account balance:

```python
# Get balance
balance = adapter.get_balance()
print(f"Balance: {balance['balance']} {balance['currency']}")
print(f"Country: {balance['country']}")
```

### KYC API

Verify customer identity:

```python
# Perform KYC inquiry
kyc_info = adapter.kyc_inquiry("254712345678")

print(f"Customer: {kyc_info.full_name}")
print(f"Verified: {kyc_info.is_verified}")
print(f"ID Number: {kyc_info.id_number}")
print(f"Grade: {kyc_info.grade}")
print(f"Registration Date: {kyc_info.registration_date}")
```

### Refund API

Refund a transaction:

```python
# Refund transaction
result = adapter.refund_transaction(
    transaction_id="AM-12345-67890",
    reference="REFUND-12345"
)

print(f"Refund status: {result['status']}")
```

### Context Manager (Recommended)

Use adapter as context manager for automatic cleanup:

```python
from airtel_money_adapter import AirtelMoneyAdapter, CountryCode

with AirtelMoneyAdapter(
    client_id="your-client-id",
    client_secret="your-client-secret",
    country=CountryCode.KENYA,
    environment="production"
) as adapter:
    # Use adapter
    balance = adapter.get_balance()
    print(f"Balance: {balance['balance']}")

# Automatically cleaned up after with block
```

## Use Cases for Microfinance

### 1. Loan Disbursement Workflow

```python
from airtel_money_adapter import AirtelMoneyAdapter, CountryCode

adapter = AirtelMoneyAdapter(
    client_id="your-client-id",
    client_secret="your-client-secret",
    country=CountryCode.KENYA,
    pin="1234"
)

# Step 1: Verify customer KYC
kyc = adapter.kyc_inquiry("254712345678")
if not kyc.is_verified:
    print("Customer not verified")
    exit(1)

# Step 2: Check lender balance
balance = adapter.get_balance()
if balance['balance'] < 5000:
    print("Insufficient balance")
    exit(1)

# Step 3: Disburse loan
result = adapter.transfer(
    amount=5000.00,
    msisdn="254712345678",
    reference="LOAN-001",
    description="Loan disbursement"
)

print(f"Loan disbursed: {result['transaction_id']}")
```

### 2. Loan Repayment Collection

```python
# Initiate USSD Push for repayment
result = adapter.ussd_push(
    amount=5500.00,  # Principal + interest
    msisdn="254712345678",
    reference="REPAY-001",
    description="Loan repayment"
)

# Customer receives prompt on their phone to enter PIN

# Monitor status
status = adapter.get_collection_status(result['transaction_id'])
if status['status'] == 'SUCCESS':
    print("Repayment received")
    # Update loan status in database
else:
    print("Repayment pending or failed")
```

### 3. Customer Onboarding

```python
# Verify customer before account creation
customers = [
    "254712345678",
    "254723456789",
    "254734567890",
]

verified = []
for phone in customers:
    kyc = adapter.kyc_inquiry(phone)
    if kyc.is_verified:
        verified.append({
            'phone': phone,
            'name': kyc.full_name,
            'id': kyc.id_number,
            'grade': kyc.grade
        })
        print(f"✓ Verified: {kyc.full_name}")
    else:
        print(f"✗ Not verified: {phone}")

print(f"\nTotal verified: {len(verified)}/{len(customers)}")
```

### 4. Bulk Disbursements

```python
import time

disbursements = [
    {"phone": "254712345678", "amount": 5000, "ref": "LOAN-001"},
    {"phone": "254723456789", "amount": 3000, "ref": "LOAN-002"},
    {"phone": "254734567890", "amount": 7500, "ref": "LOAN-003"},
]

results = []
for disb in disbursements:
    try:
        result = adapter.transfer(
            amount=disb['amount'],
            msisdn=disb['phone'],
            reference=disb['ref'],
            description="Loan disbursement"
        )
        results.append({
            'reference': disb['ref'],
            'transaction_id': result['transaction_id'],
            'status': 'SUCCESS'
        })
        print(f"✓ {disb['ref']}: {result['transaction_id']}")
    except Exception as e:
        results.append({
            'reference': disb['ref'],
            'status': 'FAILED',
            'error': str(e)
        })
        print(f"✗ {disb['ref']}: {e}")

    # Rate limiting
    time.sleep(1)

print(f"\nCompleted: {len([r for r in results if r['status'] == 'SUCCESS'])}/{len(disbursements)}")
```

## IF.bus Integration Events

The adapter emits the following events to the IF.bus:

### Authentication Events
- `airtel.auth.token_acquired` - OAuth2 token obtained
- `airtel.auth.token_failed` - Token acquisition failed

### Collections Events
- `airtel.collection.initiated` - USSD Push initiated
- `airtel.collection.success` - USSD Push successful
- `airtel.collection.failed` - USSD Push failed
- `airtel.collection.status_checked` - Collection status queried

### Disbursement Events
- `airtel.disbursement.initiated` - Transfer initiated
- `airtel.disbursement.success` - Transfer successful
- `airtel.disbursement.failed` - Transfer failed
- `airtel.disbursement.status_checked` - Transfer status queried

### Account Events
- `airtel.account.balance_checked` - Balance queried

### KYC Events
- `airtel.kyc.verified` - KYC inquiry completed

### Refund Events
- `airtel.refund.initiated` - Refund initiated

### Callback Events
- `airtel.callback.received` - Webhook callback received

### Event Payload Structure

```python
{
    "event_name": "airtel.collection.success",
    "timestamp": "2025-12-04T10:30:45.123456",
    "adapter": "airtel_money",
    "country": "KE",
    "environment": "production",
    "data": {
        "transaction_id": "AM-12345-67890",
        "reference": "ORDER-123",
        "amount": 1000.00,
        "currency": "KES",
        "msisdn": "254712345678",
        "status": "PENDING",
        "created_at": "2025-12-04T10:30:45.123456"
    }
}
```

## Webhook/Callback Handling

### 1. Verify Callback Signature

```python
from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/callbacks/airtel-money', methods=['POST'])
def airtel_callback():
    webhook_signature = request.headers.get('X-Signature')
    request_body = request.get_data(as_text=True)

    # Verify signature
    if not adapter.verify_callback_signature(webhook_signature, request_body):
        return {'error': 'Invalid signature'}, 401

    callback_data = json.loads(request_body)

    # Process callback
    adapter.handle_callback(callback_data)

    # Return success to acknowledge receipt
    return {'success': True}, 200
```

### 2. Callback Payload Example

```json
{
    "transaction": {
        "id": "AM-12345-67890",
        "status": {
            "code": "200",
            "message": "Transaction successful"
        },
        "amount": 1000.00,
        "currency": "KES",
        "msisdn": "254712345678",
        "reference": "ORDER-123",
        "airtel_money_id": "AM-REF-12345"
    }
}
```

## Exception Handling

```python
from airtel_money_adapter import (
    AirtelMoneyError,
    AuthenticationError,
    APIError,
    ValidationError,
    InsufficientBalanceError,
)

try:
    result = adapter.transfer(
        amount=5000.00,
        msisdn="254712345678",
        reference="LOAN-001",
        description="Loan disbursement"
    )
except ValidationError as e:
    print(f"Validation error: {e}")
except AuthenticationError as e:
    print(f"Auth error: {e}")
except InsufficientBalanceError as e:
    print(f"Insufficient balance: {e}")
except APIError as e:
    print(f"API error: {e}")
except AirtelMoneyError as e:
    print(f"General error: {e}")
```

## Transaction Status Codes

| Status | Meaning | Action |
|--------|---------|--------|
| PENDING | Awaiting completion | Wait for callback or poll status |
| SUCCESS | Completed successfully | Transaction complete |
| SUCCESSFUL | Completed successfully | Transaction complete |
| FAILED | Failed | Check error message |
| TIMEOUT | Request expired | Retry transaction |
| PROCESSING | Being processed | Wait for callback |
| AMBIGUOUS | Unclear status | Query transaction status |

## Phone Number Formats

All phone numbers should be in international format (E.164):

```
Kenya: +254712345678 → 254712345678
Uganda: +256700123456 → 256700123456
Tanzania: +255712345678 → 255712345678
Rwanda: +250712345678 → 250712345678
```

The adapter automatically normalizes phone numbers if they start with `0`:
```python
# These are equivalent:
adapter.ussd_push(msisdn="0712345678", ...)  # Normalized to 254712345678 (Kenya)
adapter.ussd_push(msisdn="254712345678", ...)
adapter.ussd_push(msisdn="+254712345678", ...)
```

## Validation Helpers

### Validate Phone Number

```python
from config import validate_phone_number

is_valid, error = validate_phone_number("254712345678", "KE")
if not is_valid:
    print(f"Invalid phone: {error}")
```

### Validate Amount

```python
from config import validate_amount

is_valid, error = validate_amount(1000.00, "collection", "KE")
if not is_valid:
    print(f"Invalid amount: {error}")
```

### Get Country Configuration

```python
from config import get_country_config

country = get_country_config("KE")
print(f"Country: {country.name}")
print(f"Currency: {country.currency}")
print(f"Min amount: {country.min_transaction_amount}")
print(f"Max amount: {country.max_transaction_amount}")
```

## Security Considerations

1. **API Credentials**: Never commit credentials to version control
2. **Callback Verification**: Always verify webhook signatures
3. **HTTPS**: Always use HTTPS for callback URLs in production
4. **Token Caching**: Access tokens are cached and automatically refreshed
5. **PIN Security**: Store PINs securely (environment variables, secrets manager)
6. **Rate Limiting**: Implement rate limiting on callback endpoints
7. **Idempotency**: Use unique references to prevent duplicate transactions

## Error Codes Reference

Common Airtel Money error codes:

| Code | Meaning | Resolution |
|------|---------|-----------|
| 200 | Success | - |
| 400 | Bad Request | Check request format |
| 401 | Unauthorized | Check credentials |
| 403 | Forbidden | Check permissions |
| 404 | Not Found | Check transaction ID |
| 500 | Internal Error | Retry or contact support |
| 503 | Service Unavailable | Retry after delay |

## Logging

Configure logging to monitor adapter operations:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("airtel_money_adapter")

adapter = AirtelMoneyAdapter(
    client_id="your-client-id",
    client_secret="your-client-secret",
    logger=logger
)
```

## Testing

For development/testing, use sandbox environment:

```python
adapter = AirtelMoneyAdapter(
    client_id="sandbox-client-id",
    client_secret="sandbox-client-secret",
    environment="sandbox",
    country=CountryCode.KENYA
)
```

## Production Deployment Checklist

- [ ] Use production credentials
- [ ] Set `environment="production"`
- [ ] Configure secure callback URL (HTTPS)
- [ ] Implement proper logging and monitoring
- [ ] Set up alerting for failed transactions
- [ ] Configure rate limiting on webhooks
- [ ] Enable signature verification on all callbacks
- [ ] Implement transaction status polling backup
- [ ] Set up database for transaction tracking
- [ ] Configure error notifications
- [ ] Test failover scenarios
- [ ] Document all API credentials
- [ ] Implement retry logic for failed transactions
- [ ] Set up reconciliation process
- [ ] Configure transaction limits

## Performance Characteristics

- **Token Caching**: Reduces authentication overhead
- **Connection Pooling**: HTTP session reuse
- **Retry Strategy**: Automatic retry with exponential backoff
- **Timeout**: 30 seconds (configurable)
- **Typical Response Time**: 100-500ms for status checks
- **Callback Latency**: 1-5 seconds after transaction completion

## Country-Specific Transaction Limits

| Country | Min Amount | Max Amount | Currency |
|---------|------------|------------|----------|
| Kenya | 10.00 | 150,000.00 | KES |
| Uganda | 1,000.00 | 5,000,000.00 | UGX |
| Tanzania | 1,000.00 | 10,000,000.00 | TZS |
| Rwanda | 100.00 | 5,000,000.00 | RWF |
| Zambia | 10.00 | 50,000.00 | ZMW |
| Malawi | 500.00 | 2,000,000.00 | MWK |
| Nigeria | 100.00 | 1,000,000.00 | NGN |
| DRC | 1,000.00 | 10,000,000.00 | CDF |

## API Reference

### Collections API

```python
# USSD Push
result = adapter.ussd_push(
    amount: float,
    msisdn: str,
    reference: str,
    description: str = "Payment",
    callback_url: Optional[str] = None
) -> Dict[str, Any]

# Check status
status = adapter.get_collection_status(
    transaction_id: str
) -> Dict[str, Any]
```

### Disbursements API

```python
# Transfer money
result = adapter.transfer(
    amount: float,
    msisdn: str,
    reference: str,
    description: str = "Transfer",
    pin: Optional[str] = None
) -> Dict[str, Any]

# Check status
status = adapter.get_disbursement_status(
    transaction_id: str
) -> Dict[str, Any]
```

### Account API

```python
# Get balance
balance = adapter.get_balance() -> Dict[str, Any]
```

### KYC API

```python
# KYC inquiry
kyc_info = adapter.kyc_inquiry(
    msisdn: str
) -> KYCInfo
```

### Refund API

```python
# Refund transaction
result = adapter.refund_transaction(
    transaction_id: str,
    reference: str
) -> Dict[str, Any]
```

## Troubleshooting

### Authentication Fails

1. Verify client ID and secret are correct
2. Check environment is correct (sandbox/production)
3. Ensure credentials match the environment
4. Check network connectivity

### Payments Not Processing

1. Verify phone number format (E.164)
2. Check amount is within limits
3. Confirm subscriber has sufficient balance
4. Verify subscriber's Airtel Money account is active
5. Check country configuration is correct

### Callbacks Not Received

1. Verify callback URL is reachable (HTTPS)
2. Check firewall/network configuration
3. Confirm signature verification is not rejecting valid callbacks
4. Check callback endpoint logs
5. Verify webhook is configured in Airtel dashboard

### Balance Issues

1. Check account has sufficient funds
2. Verify correct account is being used
3. Check for pending transactions
4. Contact Airtel support for account issues

## Comparison with Other Mobile Money Providers

| Feature | Airtel Money | M-Pesa | MTN MoMo |
|---------|--------------|--------|----------|
| Countries | 14 | 8+ | 11+ |
| Collections | USSD Push | STK Push | Request to Pay |
| Disbursements | Yes | B2C | Yes |
| KYC API | Yes | Limited | Limited |
| Refunds | Yes | Yes | No |
| OAuth2 | Yes | Yes | Yes |

## References

- [Airtel Money Developer Portal](https://developers.airtel.africa/)
- [Official API Documentation](https://developers.airtel.africa/documentation)
- [E.164 Phone Number Format](https://en.wikipedia.org/wiki/E.164)
- [OAuth2 Client Credentials](https://oauth.net/2/grant-types/client-credentials/)

## Support

For issues or questions:
1. Check this README
2. Review Airtel Money API documentation
3. Check adapter logs for error details
4. Contact Airtel Money support

## License

Airtel Money API Adapter - Production Ready Integration

## Changelog

### Version 1.0.0 (2025-12-04)
- Initial production release
- Support for 14 African countries
- OAuth2 authentication with token caching
- Collections API (USSD Push)
- Disbursements API
- Account API (balance, KYC)
- Refund API
- IF.bus event integration
- Comprehensive error handling
- Retry logic with exponential backoff
- Full documentation and examples

---

**Last Updated**: 2025-12-04
**Version**: 1.0.0
**Status**: Production Ready
**Coverage**: 14 African Countries
