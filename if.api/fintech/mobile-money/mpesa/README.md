# M-Pesa Daraja API Adapter

Production-ready Python adapter for Safaricom's M-Pesa Daraja API v1. Provides comprehensive functionality for payment collections, disbursements, transaction queries, and account balance operations with built-in IF.bus event integration.

## Features

- **OAuth2 Authentication**: Automatic token management with caching and expiry handling
- **STK Push (Lipa Na M-Pesa Online)**: Initiate and query payment collection prompts
- **B2C Payments**: Disbursements to customers (Salary, Business, Promotion payments)
- **Transaction Status Queries**: Check status of M-Pesa transactions
- **Account Balance**: Query business account balance
- **IF.bus Integration**: Built-in event emission for all operations
- **Automatic Retries**: Configurable retry strategy with exponential backoff
- **Environment Support**: Sandbox and production environments
- **Type Hints**: Full type annotations for better IDE support
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Error Handling**: Custom exceptions with meaningful error messages

## Setup Requirements

### 1. Obtain Daraja API Credentials

Visit [Safaricom Daraja Portal](https://developer.safaricom.co.ke/) to:

1. Create a developer account
2. Create an app to get:
   - **Consumer Key**
   - **Consumer Secret**
3. Generate an online passkey from your business account
4. Get your **Business Shortcode** (or Till Number)

### 2. Install Dependencies

```bash
pip install requests
```

For production with certificate-based encryption:

```bash
pip install requests cryptography
```

## Environment Variables

Configure the following environment variables:

```bash
# Required credentials
export MPESA_CONSUMER_KEY="your_consumer_key"
export MPESA_CONSUMER_SECRET="your_consumer_secret"
export MPESA_BUSINESS_SHORTCODE="123456"
export MPESA_PASSKEY="your_online_passkey"

# Optional
export MPESA_ENVIRONMENT="sandbox"  # or "production"
export MPESA_TIMEOUT="30"           # Request timeout in seconds
export MPESA_MAX_RETRIES="3"        # Maximum retry attempts
```

### Obtaining Credentials

#### Consumer Key & Secret
1. Log in to [Safaricom Daraja](https://developer.safaricom.co.ke/)
2. Go to "My Apps"
3. Create a new app or select existing
4. Copy Consumer Key and Consumer Secret

#### Business Shortcode
- **For M-Pesa**: Your 6-digit business shortcode
- **For Till**: Your till number
- **For PAYBILL**: Your PayBill number

#### Passkey
1. Log in to your M-Pesa Business account
2. Navigate to Settings > Online Checkout
3. Copy the online passkey (provided by Safaricom)

## Usage Examples

### Basic Setup

```python
from mpesa_adapter import MpesaAdapter, Environment, create_mpesa_adapter

# Method 1: Direct initialization
adapter = MpesaAdapter(
    consumer_key="your_key",
    consumer_secret="your_secret",
    business_shortcode="123456",
    passkey="your_passkey",
    environment=Environment.SANDBOX
)

# Method 2: From environment variables
adapter = create_mpesa_adapter(environment="sandbox")
```

### STK Push (Payment Collection)

Initiate a payment prompt on customer's phone:

```python
try:
    # Initiate STK Push
    response = adapter.initiate_stk_push(
        phone_number="254712345678",      # Customer phone (254... format)
        amount=100.00,                     # Amount in KES
        account_reference="INV001",        # Your reference ID
        transaction_desc="Payment for Order #123",
        callback_url="https://yourdomain.com/mpesa/callback"
    )

    print(f"Checkout ID: {response['CheckoutRequestID']}")
    print(f"Merchant Request ID: {response['MerchantRequestID']}")

    # Store CheckoutRequestID for later status queries
    checkout_id = response['CheckoutRequestID']

    # Query status after a short delay
    import time
    time.sleep(5)  # Wait for user to enter PIN

    status = adapter.query_stk_push_status(checkout_id)
    print(f"Transaction Status: {status['ResultDescription']}")

except Exception as e:
    print(f"Error: {e}")
```

### B2C Payment (Disbursement)

Send money from business to customer:

```python
try:
    # Salary payment
    result = adapter.b2c_payment(
        phone_number="254712345678",
        amount=5000.00,
        command_id="SalaryPayment",
        remarks="Monthly Salary",
        occasion="December 2024"
    )

    print(f"Conversation ID: {result['ConversationID']}")
    print(f"Response: {result['ResponseDescription']}")

except Exception as e:
    print(f"B2C Payment Error: {e}")
```

B2C Payment Types:

- **BusinessPayment**: General business payment
- **SalaryPayment**: Employee salary payment
- **PromotionPayment**: Promotional/bonus payment

### Query Transaction Status

Check status of a specific transaction:

```python
try:
    # Using M-Pesa receipt number
    status = adapter.query_transaction_status(
        transaction_id="LHG31AA5695"
    )

    result_code = status.get('ResultCode')
    if result_code == '0':
        print("Transaction successful!")
        print(f"Amount: {status.get('ResultParameters')}")
    else:
        print(f"Transaction failed: {status.get('ResultDescription')}")

except Exception as e:
    print(f"Status Query Error: {e}")
```

### Get Account Balance

Query your business account balance:

```python
try:
    balance_response = adapter.get_account_balance()

    print(f"Conversation ID: {balance_response['ConversationID']}")
    # Balance details will be available in the callback response

except Exception as e:
    print(f"Balance Query Error: {e}")
```

### Complete Application Example

```python
import os
import logging
from mpesa_adapter import create_mpesa_adapter, MpesaEventEmitter

# Setup logging
logging.basicConfig(level=logging.INFO)

# Custom event emitter for IF.bus integration
class IFBusEventEmitter(MpesaEventEmitter):
    def emit(self, event_name: str, data: dict):
        """Emit events to IF.bus"""
        print(f"[IF.bus] {event_name}: {data}")
        # TODO: Integrate with actual IF.bus infrastructure
        # bus.emit(event_name, data)

# Initialize adapter
try:
    emitter = IFBusEventEmitter()
    adapter = create_mpesa_adapter(
        environment="sandbox",
        event_emitter=emitter
    )

    # Process payment
    result = adapter.initiate_stk_push(
        phone_number="254712345678",
        amount=100.00,
        account_reference="ORDER_001"
    )

    print(f"STK Push Initiated: {result['CheckoutRequestID']}")

except Exception as e:
    print(f"Error: {e}")
finally:
    adapter.close()
```

## IF.bus Event Integration

The adapter emits the following events to IF.bus:

### Authentication Events
- **mpesa.auth.token_acquired**: Access token successfully obtained
  ```json
  {
    "timestamp": "2024-12-04T10:30:00",
    "environment": "sandbox"
  }
  ```

### STK Push Events
- **mpesa.stk_push.initiated**: STK Push prompt sent to customer
  ```json
  {
    "phone_number": "254712345678",
    "amount": 100.0,
    "account_reference": "INV001",
    "merchant_request_id": "...",
    "checkout_request_id": "...",
    "timestamp": "20241204103000"
  }
  ```

- **mpesa.stk_push.success**: STK Push payment successful
  ```json
  {
    "checkout_request_id": "...",
    "result_code": "0",
    "result_description": "The service request has been accepted successfully."
  }
  ```

- **mpesa.stk_push.failed**: STK Push payment failed
  ```json
  {
    "checkout_request_id": "...",
    "result_code": "1",
    "result_description": "..."
  }
  ```

### B2C Payment Events
- **mpesa.b2c.initiated**: B2C payment initiated
  ```json
  {
    "phone_number": "254712345678",
    "amount": 5000.0,
    "command_id": "SalaryPayment",
    "conversation_id": "...",
    "originator_conversation_id": "...",
    "timestamp": "20241204103000"
  }
  ```

- **mpesa.b2c.success**: B2C payment completed
- **mpesa.b2c.failed**: B2C payment failed

### Query Events
- **mpesa.transaction.status_query**: Transaction status queried
  ```json
  {
    "transaction_id": "LHG31AA5695",
    "result_code": "0",
    "timestamp": "20241204103000"
  }
  ```

- **mpesa.balance.query**: Account balance queried
  ```json
  {
    "timestamp": "20241204103000",
    "conversation_id": "..."
  }
  ```

### Error Events
- **mpesa.error.occurred**: Any error during operations
  ```json
  {
    "error_type": "stk_push_failed",
    "message": "Error description",
    "phone_number": "254712345678"
  }
  ```

### Integrating with IF.bus

```python
from mpesa_adapter import MpesaEventEmitter, MpesaAdapter

class IFBusEmitter(MpesaEventEmitter):
    def __init__(self, bus):
        self.bus = bus

    def emit(self, event_name: str, data: dict):
        """Emit M-Pesa events to IF.bus"""
        self.bus.emit(event_name, data)

# Usage with IF.bus
from if_bus import Bus

bus = Bus()
emitter = IFBusEmitter(bus)

adapter = MpesaAdapter(
    consumer_key="...",
    consumer_secret="...",
    business_shortcode="...",
    passkey="...",
    event_emitter=emitter
)
```

## Error Handling

The adapter provides custom exceptions for different error scenarios:

```python
from mpesa_adapter import MpesaAdapter, MpesaAuthException, MpesaAPIException, MpesaException

try:
    adapter = MpesaAdapter(...)
    result = adapter.initiate_stk_push(...)

except MpesaAuthException as e:
    # Authentication failure
    print(f"Auth failed: {e}")

except MpesaAPIException as e:
    # API call failure
    print(f"API error: {e}")

except MpesaException as e:
    # General M-Pesa error
    print(f"M-Pesa error: {e}")
```

## Retry Strategy

The adapter automatically retries failed requests with exponential backoff:

- **Max Retries**: Configurable (default: 3)
- **Backoff Factor**: 1 second
- **Retryable Status Codes**: 429, 500, 502, 503, 504

```python
adapter = MpesaAdapter(
    consumer_key="...",
    consumer_secret="...",
    business_shortcode="...",
    passkey="...",
    max_retries=5,      # Increase retry attempts
    timeout=60          # Increase timeout to 60 seconds
)
```

## Phone Number Format

All phone numbers must be in international format:

- **Valid**: `254712345678` (Kenya +254)
- **Invalid**: `0712345678`, `+254712345678`, `712345678`

To convert:
```python
def format_phone(phone: str) -> str:
    """Convert phone number to international format."""
    if phone.startswith('0'):
        return '254' + phone[1:]
    elif phone.startswith('+'):
        return phone[1:]
    return phone
```

## Amount Format

All amounts should be provided as floats in KES (Kenyan Shilling):

```python
adapter.initiate_stk_push(
    phone_number="254712345678",
    amount=100.50,      # Will be converted to 100 (integer) internally
    account_reference="REF001"
)
```

## Production Deployment Checklist

- [ ] Use production credentials from Safaricom
- [ ] Set `Environment.PRODUCTION` in adapter initialization
- [ ] Implement proper certificate-based encryption for security credentials
- [ ] Configure valid callback URLs for async responses
- [ ] Implement webhook handlers for payment confirmations
- [ ] Set up proper error logging and monitoring
- [ ] Configure IF.bus integration for event tracking
- [ ] Add rate limiting for STK Push requests
- [ ] Implement idempotency handling for duplicate requests
- [ ] Set up alerting for failed transactions
- [ ] Test with actual M-Pesa accounts
- [ ] Review Safaricom's security guidelines

## Security Considerations

1. **Credentials**: Never hardcode credentials. Use environment variables.
2. **Certificate**: Implement proper certificate-based encryption for production.
3. **HTTPS**: All API calls use HTTPS. Verify SSL certificates.
4. **Timeout**: Configure appropriate timeouts to avoid hanging requests.
5. **Logging**: Be careful not to log sensitive data (tokens, passwords, etc.).
6. **Callback Security**: Validate callback signatures from M-Pesa.
7. **Rate Limiting**: Implement rate limiting on STK Push to prevent abuse.

## Logging

Configure logging to monitor adapter operations:

```python
import logging

# Set adapter logger level
logging.getLogger('mpesa_adapter').setLevel(logging.DEBUG)

# Or configure all logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## API Rate Limits

Safaricom enforces rate limits on Daraja API:

- **STK Push**: Recommended max 20 requests per minute per shortcode
- **B2C**: No strict limit, but monitor for throttling
- **Queries**: No strict limit

## Testing

### Sandbox Testing Phone Numbers

Test with these numbers in sandbox:
- `254712345678`
- `254708374149`
- `254706092517`

### Test Amounts

- Any amount works in sandbox
- Use realistic amounts for testing (e.g., 1-5000 KES)

### Expected Responses

In sandbox, STK Push will complete automatically after ~5 seconds with:
- **ResultCode**: "0" (Success)
- **MpesaReceiptNumber**: Auto-generated receipt

## Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Check consumer key and secret
   - Verify credentials in Daraja portal

2. **Business Shortcode Invalid**
   - Verify shortcode format (6 digits)
   - Ensure shortcode is active in Daraja settings

3. **Passkey Invalid**
   - Get fresh passkey from M-Pesa Business account
   - Ensure passkey matches online checkout setting

4. **Transaction Timeout**
   - Increase timeout in adapter configuration
   - Check network connectivity
   - Verify callback URL is accessible

5. **Rate Limit (429 Response)**
   - Reduce frequency of requests
   - Implement request queuing

## References

- [Safaricom Daraja API Documentation](https://developer.safaricom.co.ke/)
- [M-Pesa API Guides](https://developer.safaricom.co.ke/Documentation)
- [M-Pesa Integration Guide](https://developer.safaricom.co.ke/docs)

## Support

For issues or questions:

1. Check Safaricom Daraja documentation
2. Review error logs from adapter logging
3. Test in sandbox environment first
4. Contact Safaricom developer support

## License

This adapter is part of the InfraFabric (IF.api) fintech module.
