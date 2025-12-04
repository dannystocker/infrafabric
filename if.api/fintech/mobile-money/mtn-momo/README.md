# MTN Mobile Money (MoMo) API Adapter

Production-ready Python adapter for MTN Mobile Money APIs, providing seamless integration with MTN's mobile financial services across 11+ African countries.

## Features

- **Collections API**: Request payment from mobile subscribers (invoice/request to pay)
- **Disbursements API**: Transfer money to subscribers' mobile wallets
- **Remittances API**: Cross-border money transfers between countries
- **OAuth2 Authentication**: Automatic token management with caching
- **API User Management**: Create and manage API users programmatically
- **Transaction Status Monitoring**: Check status of payments and transfers
- **Webhook Callbacks**: Receive and verify transaction notifications
- **IF.bus Integration**: Full event emission for transaction lifecycle
- **Multi-country Support**: Uganda, Ghana, Cameroon, DRC, Benin, Guinea, and more
- **Type Hints & Docstrings**: Full type safety and documentation
- **Error Handling**: Comprehensive exception handling with custom exceptions
- **Sandbox & Production**: Support for both environments

## Supported Countries

| Country | Code | Endpoint |
|---------|------|----------|
| Uganda | UG | https://openapi.mtn.com/collection/v1_0 |
| Ghana | GH | https://openapi.mtn.com/collection/v1_0 |
| Cameroon | CM | https://openapi.mtn.com/collection/v1_0 |
| Ivory Coast | CI | https://openapi.mtn.com/collection/v1_0 |
| DRC | CD | https://openapi.mtn.com/collection/v1_0 |
| Benin | BJ | https://openapi.mtn.com/collection/v1_0 |
| Guinea | GN | https://openapi.mtn.com/collection/v1_0 |
| Guinea-Bissau | GW | https://openapi.mtn.com/collection/v1_0 |
| Mozambique | MZ | https://openapi.mtn.com/collection/v1_0 |
| Tanzania | TZ | https://openapi.mtn.com/collection/v1_0 |
| Rwanda | RW | https://openapi.mtn.com/collection/v1_0 |

## Installation

### Requirements

- Python 3.8+
- `requests` library

### Setup

```bash
pip install requests
```

## Configuration

### Step 1: Create API User (One-time Setup)

Before using the adapter, you need credentials from MTN Developer Portal.

```python
from mtn_momo_adapter import MTNMoMoAdapter, CountryCode

# Create API user using provisioning key
adapter = MTNMoMoAdapter(
    subscription_key="your-subscription-key",
    api_user="temp-user",  # Can be any value for initial setup
    api_key="temp-key",
    country=CountryCode.UGANDA,
    environment="sandbox"
)

# Create API user (requires provisioning key from MTN)
api_user_id = adapter.create_api_user(
    provisioning_key="your-provisioning-key",
    reference_id="my-api-user-001"
)

print(f"API User created: {api_user_id}")
```

### Step 2: Get API Credentials

After creating the API user, obtain API key from MTN dashboard:

```
Subscription Key (Ocp-Apim-Subscription-Key): <your-subscription-key>
API User: <api-user-id>
API Key: <api-key-from-dashboard>
```

### Step 3: Configure Environment Variables

Create `.env` file in your application:

```env
# MTN MoMo Configuration
MTN_SUBSCRIPTION_KEY=your-subscription-key
MTN_API_USER=your-api-user-id
MTN_API_KEY=your-api-key
MTN_COUNTRY=UG  # Country code (UG, GH, CM, etc.)
MTN_ENVIRONMENT=production  # or "sandbox"
MTN_CALLBACK_URL=https://your-domain.com/callbacks/mtn-momo
```

### Step 4: Initialize Adapter

```python
import os
from mtn_momo_adapter import MTNMoMoAdapter, CountryCode

adapter = MTNMoMoAdapter(
    subscription_key=os.getenv("MTN_SUBSCRIPTION_KEY"),
    api_user=os.getenv("MTN_API_USER"),
    api_key=os.getenv("MTN_API_KEY"),
    country=CountryCode[os.getenv("MTN_COUNTRY", "UG")],
    environment=os.getenv("MTN_ENVIRONMENT", "sandbox"),
    callback_url=os.getenv("MTN_CALLBACK_URL"),
)
```

## Usage Examples

### Collections API (Request to Pay)

Request payment from a subscriber:

```python
# Request payment
result = adapter.request_to_pay(
    amount="100.00",
    payer_msisdn="256700123456",  # E.164 format
    description="Payment for Order #12345",
    external_id="order-12345",  # Your unique reference
    payee_note="Thank you for your purchase",
    payer_note="Order payment",
    currency="EUR"
)

print(f"Transaction ID: {result['transaction_id']}")
print(f"Status: {result['status']}")  # PENDING

# Check payment status
status = adapter.check_collection_status(result['transaction_id'])
print(f"Current status: {status['status']}")  # SUCCESSFUL, FAILED, PENDING, etc.

if status['status'] == 'FAILED':
    print(f"Failure reason: {status['reason_message']}")
```

### Disbursements API (Money Transfer)

Send money to a subscriber:

```python
# Transfer money
result = adapter.transfer_money(
    amount="50.00",
    recipient_msisdn="256701234567",
    description="Salary payment",
    external_id="salary-emp-001",
    payee_note="Your monthly salary",
    currency="EUR"
)

print(f"Transfer ID: {result['transaction_id']}")

# Check transfer status
status = adapter.check_transfer_status(result['transaction_id'])
print(f"Transfer status: {status['status']}")
```

### Remittances API (Cross-border Transfers)

Send money across borders:

```python
# Send remittance from Uganda to Ghana
result = adapter.send_remittance(
    amount="200.00",
    recipient_msisdn="233550123456",  # Ghana number
    recipient_country=CountryCode.GHANA,
    description="Family remittance",
    external_id="remit-fam-001",
    sender_currency="EUR",
    recipient_currency="GHS"  # Optional
)

print(f"Remittance ID: {result['transaction_id']}")

# Check remittance status
status = adapter.check_remittance_status(result['transaction_id'])
print(f"Remittance status: {status['status']}")
print(f"Recipient country: {status['payee_country']}")
```

### Context Manager (Recommended)

Use adapter as context manager for automatic cleanup:

```python
from mtn_momo_adapter import MTNMoMoAdapter, CountryCode

with MTNMoMoAdapter(
    subscription_key="...",
    api_user="...",
    api_key="...",
    country=CountryCode.UGANDA
) as adapter:
    # Use adapter
    result = adapter.request_to_pay(
        amount="100.00",
        payer_msisdn="256700123456",
        description="Payment"
    )
    print(result)

# Automatically cleaned up after with block
```

## Webhook/Callback Handling

### 1. Verify Callback Signature

```python
from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/callbacks/mtn-momo', methods=['POST'])
def mtn_callback():
    webhook_signature = request.headers.get('X-Signature')
    request_body = request.get_data(as_text=True)

    # Verify signature
    if not adapter.verify_callback_signature(webhook_signature, request_body):
        return {'error': 'Invalid signature'}, 401

    callback_data = json.loads(request_body)

    # Process based on transaction type
    if callback_data.get('type') == 'collection':
        adapter.handle_collection_notification(callback_data)
    elif callback_data.get('type') == 'disbursement':
        adapter.handle_disbursement_notification(callback_data)

    # Return success to acknowledge receipt
    return {'success': True}, 200
```

### 2. Callback Payload Example

**Collections Callback:**
```json
{
    "externalId": "order-12345",
    "transactionId": "mtn-txn-001",
    "status": "SUCCESSFUL",
    "amount": "100.00",
    "currency": "EUR",
    "payer": {
        "partyIdType": "MSISDN",
        "partyId": "256700123456"
    },
    "payee": {
        "partyIdType": "MSISDN",
        "partyId": "256705000000"
    },
    "description": "Payment for Order #12345",
    "reason": {
        "code": "00",
        "message": "Transaction successful"
    }
}
```

**Disbursement Callback:**
```json
{
    "externalId": "salary-emp-001",
    "transactionId": "mtn-txn-002",
    "status": "SUCCESSFUL",
    "amount": "50.00",
    "currency": "EUR",
    "payer": {
        "partyIdType": "MSISDN",
        "partyId": "256705000000"
    },
    "payee": {
        "partyIdType": "MSISDN",
        "partyId": "256701234567"
    },
    "description": "Salary payment",
    "reason": null
}
```

## IF.bus Integration Events

The adapter emits the following events to the IF.bus:

### Authentication Events
- `mtn.momo.auth.token_requested` - OAuth2 token acquired
- `mtn.momo.auth.token_failed` - Token acquisition failed
- `mtn.momo.auth.api_user_created` - API user created
- `mtn.momo.auth.api_user_creation_failed` - API user creation failed

### Collections Events
- `mtn.momo.collection.request_initiated` - Payment request started
- `mtn.momo.collection.request_sent` - Payment request sent to API
- `mtn.momo.collection.request_failed` - Payment request failed
- `mtn.momo.collection.status_checked` - Payment status queried
- `mtn.momo.collection.notification_received` - Webhook callback received

### Disbursement Events
- `mtn.momo.disbursement.transfer_initiated` - Transfer started
- `mtn.momo.disbursement.transfer_sent` - Transfer sent to API
- `mtn.momo.disbursement.transfer_failed` - Transfer failed
- `mtn.momo.disbursement.status_checked` - Transfer status queried
- `mtn.momo.disbursement.notification_received` - Webhook callback received

### Remittance Events
- `mtn.momo.remittance.transfer_initiated` - Remittance started
- `mtn.momo.remittance.transfer_sent` - Remittance sent to API
- `mtn.momo.remittance.transfer_failed` - Remittance failed
- `mtn.momo.remittance.status_checked` - Remittance status queried
- `mtn.momo.remittance.notification_received` - Webhook callback received

### Event Payload Structure

```python
{
    "event_name": "mtn.momo.collection.request_sent",
    "timestamp": "2025-12-04T10:30:45.123456",
    "adapter": "mtn_momo",
    "country": "UG",
    "data": {
        "transaction_id": "12345",
        "external_id": "order-123",
        "amount": "100.00",
        "currency": "EUR",
        "payer": "256700123456",
        "status": "PENDING",
        "created_at": "2025-12-04T10:30:45.123456"
    }
}
```

## Exception Handling

```python
from mtn_momo_adapter import (
    MTNMoMoError,
    AuthenticationError,
    APIError,
    ValidationError,
    CallbackError,
)

try:
    result = adapter.request_to_pay(
        amount="100.00",
        payer_msisdn="256700123456",
        description="Payment"
    )
except ValidationError as e:
    print(f"Validation error: {e}")
except AuthenticationError as e:
    print(f"Auth error: {e}")
except APIError as e:
    print(f"API error: {e}")
except MTNMoMoError as e:
    print(f"General error: {e}")
```

## Transaction Status Codes

| Status | Meaning | Action |
|--------|---------|--------|
| PENDING | Awaiting completion | Wait for callback |
| SUCCESSFUL | Completed successfully | Transaction done |
| FAILED | Failed | Check error_code/message |
| REJECTED | Rejected by subscriber | Notify user |
| EXPIRED | Request expired | Create new request |
| PROCESSING | Being processed | Wait for callback |

## Country-Specific Considerations

### Phone Number Formats

All phone numbers should be in E.164 format (with country code):

```
Uganda: +256XXXXXXXXX → 256XXXXXXXXX
Ghana: +233XXXXXXXXX → 233XXXXXXXXX
Cameroon: +237XXXXXXXXX → 237XXXXXXXXX
DRC: +243XXXXXXXXX → 243XXXXXXXXX
```

### Currency Codes

- **Uganda**: EUR (or UGX for local)
- **Ghana**: EUR (or GHS for local)
- **Cameroon**: EUR (or XAF for local)
- **DRC**: EUR (or CDF for local)

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Callback Verification**: Always verify webhook signatures before processing
3. **HTTPS**: Always use HTTPS for callback URLs in production
4. **Token Caching**: Access tokens are cached and automatically refreshed
5. **Rate Limiting**: Implement rate limiting on callback endpoints
6. **Idempotency**: Use `external_id` to prevent duplicate transactions

## Error Codes Reference

Common MTN MoMo error codes:

| Code | Meaning | Resolution |
|------|---------|-----------|
| 00 | Success | - |
| 01 | Invalid transaction | Check transaction details |
| 02 | Invalid merchant | Verify merchant credentials |
| 03 | Invalid request | Check request format |
| 04 | Insufficient balance | Check wallet balance |
| 05 | Transaction expired | Create new transaction |
| 06 | Declined | Check with MTN support |

## Logging

Configure logging to monitor adapter operations:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("mtn_momo_adapter")

adapter = MTNMoMoAdapter(
    subscription_key="...",
    api_user="...",
    api_key="...",
    logger=logger
)
```

## Testing

For development/testing, use sandbox environment:

```python
adapter = MTNMoMoAdapter(
    subscription_key="sandbox-key",
    api_user="sandbox-user",
    api_key="sandbox-key",
    environment="sandbox"
)
```

## Production Deployment Checklist

- [ ] Use production credentials from MTN dashboard
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
- [ ] Document all API user accounts

## Performance Characteristics

- **Token Caching**: Reduces authentication overhead
- **Connection Pooling**: HTTP session reuse
- **Timeout**: 30 seconds (configurable)
- **Typical Response Time**: 100-500ms for status checks
- **Callback Latency**: 1-5 seconds after transaction completion

## API Reference

### Collections API

```python
# Request payment
result = adapter.request_to_pay(
    amount: str,
    payer_msisdn: str,
    description: str,
    external_id: Optional[str] = None,
    payee_note: Optional[str] = None,
    payer_note: Optional[str] = None,
    currency: str = "EUR"
) -> Dict[str, Any]

# Check status
status = adapter.check_collection_status(
    reference_id: str
) -> Dict[str, Any]
```

### Disbursements API

```python
# Transfer money
result = adapter.transfer_money(
    amount: str,
    recipient_msisdn: str,
    description: str,
    external_id: Optional[str] = None,
    payee_note: Optional[str] = None,
    payer_note: Optional[str] = None,
    currency: str = "EUR"
) -> Dict[str, Any]

# Check status
status = adapter.check_transfer_status(
    reference_id: str
) -> Dict[str, Any]
```

### Remittances API

```python
# Send cross-border transfer
result = adapter.send_remittance(
    amount: str,
    recipient_msisdn: str,
    recipient_country: CountryCode,
    description: str,
    external_id: Optional[str] = None,
    sender_currency: str = "EUR",
    recipient_currency: Optional[str] = None
) -> Dict[str, Any]

# Check status
status = adapter.check_remittance_status(
    reference_id: str
) -> Dict[str, Any]
```

## Troubleshooting

### Authentication Fails

1. Verify subscription key is correct
2. Check API user and key are valid
3. Ensure API user has correct permissions
4. Verify environment matches (sandbox/production)

### Payments Not Processing

1. Verify phone number format (E.164)
2. Check amount is valid
3. Confirm payer has sufficient balance
4. Review MTN support for account status

### Callbacks Not Received

1. Verify callback URL is reachable (HTTPS)
2. Check firewall/network configuration
3. Confirm signature verification is not rejecting valid callbacks
4. Check callback endpoint logs

## References

- [MTN MoMo Developer Portal](https://momodeveloper.mtn.com/)
- [Official API Documentation](https://momodeveloper.mtn.com/documentation)
- [E.164 Phone Number Format](https://en.wikipedia.org/wiki/E.164)

## License

MTN MoMo API Adapter - Production Ready Integration

## Support

For issues or questions:
1. Check this README
2. Review MTN MoMo API documentation
3. Check adapter logs for error details
4. Contact MTN MoMo support

---

**Last Updated**: 2025-12-04
**Version**: 1.0.0
**Status**: Production Ready
