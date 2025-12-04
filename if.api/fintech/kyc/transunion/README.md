# TransUnion Africa Credit Bureau API Adapter

**Version:** 1.0.0
**Status:** Production Ready
**Market Focus:** Kenya (Primary), Uganda, Tanzania, Rwanda, South Africa, Nigeria, Ghana
**Framework:** InfraFabric IF.bus Integration
**Author:** InfraFabric FinTech Integration
**Date:** 2025-12-04

---

## Overview

Production-ready Python adapter for TransUnion Africa Credit Bureau API services. Enables seamless integration with TransUnion's credit reporting, ID verification, fraud detection, and loan performance reporting systems across African markets.

### Key Features

- **Multi-Market Support**: Kenya, Uganda, Tanzania, Rwanda, South Africa, Nigeria, Ghana
- **Multiple Authentication Methods**: OAuth2, API Key, Certificate-based
- **Comprehensive Operations**:
  - Credit report queries (individual)
  - Credit score retrieval (quick checks)
  - ID verification
  - Fraud detection and risk scoring
  - Loan performance data submission
- **Production-Grade**:
  - Automatic session management with reconnection
  - Request validation and retry logic
  - Timeout management with exponential backoff
  - Thread-safe operation
  - Comprehensive error handling
- **IF.bus Integration**: Event emission for audit trails and monitoring
- **Type Hints & Documentation**: Full type annotations and docstrings

---

## Setup Requirements

### 1. TransUnion API Credentials

Contact TransUnion Africa regional office to obtain:

**For OAuth2 Authentication:**
- `client_id` - OAuth2 client identifier
- `client_secret` - OAuth2 client secret
- API endpoint URL (market-specific)

**For API Key Authentication:**
- `api_key` - Long-lived API key
- API endpoint URL

**For Certificate Authentication:**
- Client certificate file (.pem or .p12)
- Certificate password (if required)
- CA bundle for server verification

### 2. Python Dependencies

```bash
pip install requests>=2.28.0 urllib3>=1.26.0
```

Or with the full IF.api stack:

```bash
pip install -r /home/setup/infrafabric/if.api/requirements.txt
```

### 3. Network Configuration

- **Firewall Rules**: Ensure outbound HTTPS (443) to TransUnion endpoints
- **DNS Resolution**: Verify DNS can resolve TransUnion domains:
  - `api.transunion.co.ke` (Kenya)
  - `api.transunion.co.ug` (Uganda)
  - `api.transunion.tz` (Tanzania)
  - `api.transunion.co.za` (South Africa)
  - Similar for other markets

### 4. SSL Certificate (if required)

Some deployments may require:

```bash
# Copy certificate to secure location
cp /path/to/transunion-cert.pem /etc/ssl/certs/transunion-cert.pem
chmod 600 /etc/ssl/certs/transunion-cert.pem
```

Update adapter initialization:
```python
adapter = TransUnionAdapter(
    auth_type="certificate",
    certificate_path="/etc/ssl/certs/transunion-cert.pem",
    market="ke"
)
```

---

## Environment Variables

Create `.env` file in your application root:

```bash
# TransUnion API Configuration
TRANSUNION_MARKET=ke
TRANSUNION_ENVIRONMENT=production
TRANSUNION_AUTH_TYPE=oauth2

# OAuth2 Credentials (choose one auth method)
TRANSUNION_CLIENT_ID=your_client_id_here
TRANSUNION_CLIENT_SECRET=your_client_secret_here

# OR API Key
TRANSUNION_API_KEY=your_api_key_here

# OR Certificate Path
TRANSUNION_CERTIFICATE_PATH=/etc/ssl/certs/transunion-cert.pem

# Request Configuration
TRANSUNION_TIMEOUT=30
TRANSUNION_MAX_RETRIES=3

# Logging
TRANSUNION_LOG_LEVEL=INFO

# IF.bus Integration
IFBUS_ENABLED=true
IFBUS_REDIS_URL=redis://localhost:6379
```

Load in Python:

```python
import os
from dotenv import load_dotenv

load_dotenv()

adapter = TransUnionAdapter(
    auth_type=os.getenv("TRANSUNION_AUTH_TYPE", "oauth2"),
    client_id=os.getenv("TRANSUNION_CLIENT_ID"),
    client_secret=os.getenv("TRANSUNION_CLIENT_SECRET"),
    api_key=os.getenv("TRANSUNION_API_KEY"),
    market=os.getenv("TRANSUNION_MARKET", "ke"),
    environment=os.getenv("TRANSUNION_ENVIRONMENT", "sandbox"),
    timeout=int(os.getenv("TRANSUNION_TIMEOUT", "30")),
    max_retries=int(os.getenv("TRANSUNION_MAX_RETRIES", "3"))
)
```

---

## Compliance Requirements

### Data Protection & Privacy

1. **Personal Data Protection Act (PDPA)**
   - Kenya: Data Protection Act 2019
   - Uganda: Data Protection and Privacy Act 2019
   - Tanzania: Data Protection Act 2022
   - Ensure consent before querying individuals' credit reports
   - Implement data minimization (only request necessary fields)

2. **Encryption**
   - All data in transit must use TLS 1.2+
   - Sensitive data at rest must be encrypted (AES-256)
   - API credentials stored securely (environment variables, vaults)

3. **Access Control**
   - Implement role-based access control (RBAC)
   - Log all API accesses with timestamp and user identification
   - Restrict API credentials to minimum required scope

4. **Audit Trails**
   - Use IF.bus event system for comprehensive audit logs
   - Maintain logs for minimum 7 years (regulatory requirement)
   - Include: timestamp, user, operation, result, IP address

5. **Consent Management**
   - Obtain explicit written consent before credit inquiries
   - Store consent records with timestamp and method
   - Provide easy opt-out mechanism
   - Comply with fair information practices

### API Rate Limits

- Typical limits: 100-1000 requests/minute (varies by subscription)
- Implement exponential backoff for 429 responses
- Monitor rate limit headers in responses
- Queue requests during high-load periods

### Data Retention

- Query results: Retain per data protection laws (typically 3-7 years)
- Request logs: Permanent audit trail
- Personal data: Delete/anonymize after retention period
- Implement data purge procedures

---

## Usage Examples

### Basic Authentication and Connection

```python
from transunion_adapter import TransUnionAdapter

# Initialize adapter
adapter = TransUnionAdapter(
    auth_type="oauth2",
    client_id="your_client_id",
    client_secret="your_client_secret",
    market="ke",
    environment="production"
)

# Connect
try:
    adapter.connect()
    print(f"Connected: {adapter.get_connection_state()}")
except Exception as e:
    print(f"Connection failed: {e}")
    exit(1)

# ... perform operations ...

# Disconnect
adapter.disconnect()
```

### Get Credit Report

```python
from transunion_adapter import TransUnionAdapter

adapter = TransUnionAdapter(
    auth_type="api_key",
    api_key="sk_test_1234567890abcdef",
    market="ke"
)
adapter.connect()

try:
    # Retrieve full credit report
    report = adapter.get_credit_report(
        id_type="national_id",
        id_number="12345678",
        first_name="John",
        last_name="Doe",
        query_type="full_report",
        include_history=True
    )

    print(f"Subject ID: {report.subject_id}")
    print(f"Credit Score: {report.score.score} ({report.score.rating})")
    print(f"Status: {report.status}")
    print(f"Accounts: {report.accounts_count}")
    print(f"Total Debt: KES {report.total_debt:,.2f}")
    print(f"Delinquent Accounts: {report.delinquent_accounts}")

except Exception as e:
    print(f"Error: {e}")
finally:
    adapter.disconnect()
```

### Quick Credit Score Check

```python
# Get score only (faster operation)
try:
    score = adapter.get_credit_score(
        id_type="national_id",
        id_number="12345678",
        first_name="John",
        last_name="Doe"
    )

    print(f"Score: {score.score}")
    print(f"Rating: {score.rating}")
    print(f"Confidence: {score.confidence * 100:.1f}%")

except Exception as e:
    print(f"Error: {e}")
```

### Verify Identity

```python
try:
    result = adapter.verify_id(
        id_type="national_id",
        id_number="12345678",
        first_name="John",
        last_name="Doe",
        date_of_birth="1990-01-15",
        country_code="KE"
    )

    print(f"Verification ID: {result.verification_id}")
    print(f"Status: {result.status.value}")
    print(f"Name Match: {result.name_match}")
    print(f"Confidence: {result.confidence * 100:.1f}%")

    if result.status.value == "verified":
        print("ID verified successfully")
    elif result.status.value == "failed":
        print("ID verification failed")

except Exception as e:
    print(f"Error: {e}")
```

### Fraud Detection Check

```python
try:
    fraud_result = adapter.check_fraud(
        id_type="national_id",
        id_number="12345678",
        first_name="John",
        last_name="Doe",
        phone="+254712345678",
        email="john.doe@example.com"
    )

    print(f"Check ID: {fraud_result.check_id}")
    print(f"Risk Level: {fraud_result.risk_level}")
    print(f"Risk Score: {fraud_result.risk_score * 100:.1f}%")

    if fraud_result.alerts:
        print(f"Alerts found: {len(fraud_result.alerts)}")
        for alert in fraud_result.alerts:
            print(f"  - {alert.get('type')}: {alert.get('message')}")

except Exception as e:
    print(f"Error: {e}")
```

### Submit Loan Performance Data

```python
try:
    success = adapter.submit_loan_performance(
        subject_id="SUBJ-12345678",
        loan_id="LOAN-2025-001",
        principal=500000.00,
        interest_rate=15.5,
        term_months=24,
        disbursement_date="2025-01-15",
        current_balance=450000.00,
        payment_status="current",
        delinquent_days=0,
        metadata={
            "lender_name": "Example Bank",
            "product_type": "personal_loan",
            "currency": "KES"
        }
    )

    if success:
        print("Loan performance data submitted successfully")
    else:
        print("Loan performance submission failed")

except Exception as e:
    print(f"Error: {e}")
```

### Event Handling (IF.bus Integration)

```python
# Register event handlers
def on_authenticated(event):
    print(f"Authenticated: {event}")

def on_credit_report_retrieved(event):
    print(f"Report retrieved: query_id={event['query_id']}, score={event['score']}")

def on_error(event):
    print(f"Error: {event['error']} [{event['error_type']}]")

adapter.on("authenticated", on_authenticated)
adapter.on("credit_report_retrieved", on_credit_report_retrieved)
adapter.on("error", on_error)

# Connect and operations will now emit events
adapter.connect()
report = adapter.get_credit_report(...)
adapter.disconnect()
```

### Health Checks

```python
# Check API health
try:
    health = adapter.health_check()
    print(f"API Status: {health.get('status')}")

except Exception as e:
    print(f"API unhealthy: {e}")

# Get adapter statistics
stats = adapter.get_stats()
print(f"Requests: {stats['request_count']}")
print(f"Errors: {stats['error_count']}")
print(f"Error Rate: {stats['error_rate'] * 100:.2f}%")
print(f"Health: {stats['health_status']}")
```

---

## IF.bus Integration Events

The adapter emits the following events to IF.bus for monitoring and audit:

### Authentication Events

```
IF.bus:kyc:transunion:authenticated
  - auth_type: str (oauth2, api_key, certificate)
  - timestamp: str (ISO 8601)
  - market: str (ke, ug, tz, etc.)
```

### Query Events

```
IF.bus:kyc:transunion:credit_report_retrieved
  - query_id: str (unique query identifier)
  - subject_id: str (subject/customer ID)
  - score: int (credit score)
  - status: str (active, closed, disputed)
  - timestamp: str

IF.bus:kyc:transunion:score_retrieved
  - score: int
  - rating: str (Good, Fair, Poor)
  - confidence: float (0.0-1.0)
  - timestamp: str
```

### Verification Events

```
IF.bus:kyc:transunion:id_verified
  - verification_id: str
  - status: str (verified, failed, pending)
  - id_type: str
  - name_match: bool
  - confidence: float
  - timestamp: str
```

### Fraud Check Events

```
IF.bus:kyc:transunion:fraud_check_completed
  - check_id: str
  - risk_level: str (low, medium, high)
  - risk_score: float (0.0-1.0)
  - alert_count: int
  - timestamp: str
```

### Data Submission Events

```
IF.bus:kyc:transunion:data_submitted
  - submission_id: str
  - loan_id: str
  - success: bool
  - timestamp: str
```

### Connection Events

```
IF.bus:kyc:transunion:connection_state_changed
  - state: str (connected, disconnected, error)
  - timestamp: str

IF.bus:kyc:transunion:error
  - error: str (error message)
  - error_type: str (connection_error, api_error, validation_error, etc.)
  - context: str (operation context)
  - timestamp: str
```

---

## Alternative Credit Bureaus

### Metropol Kenya

- **Website**: https://www.metropol.co.ke/
- **Focus**: Kenya's leading credit reference bureau
- **Operations**: Credit reports, ID verification
- **Integration**: Similar API patterns, IF.adapter approach

### CRB Africa

- **Website**: https://crbafrica.com/
- **Focus**: Pan-African credit bureau network
- **Operations**: Credit reports, bureau lookups across markets
- **Integration**: Multi-country adapter available

### Smile Identity (Africa-Wide)

- **Website**: https://www.smileidentity.com/
- **Focus**: Digital identity verification across Africa
- **Operations**: ID verification, KYC services
- **Note**: Located at `/home/setup/infrafabric/if.api/fintech/kyc/smile-identity/`

### Experian Africa

- **Website**: https://www.experian.co.ke/
- **Focus**: Risk assessment, credit reporting
- **Markets**: Kenya, South Africa, and expanding
- **Operations**: Full reports, compliance services

### Choosing the Right Bureau

| Bureau | Strength | Markets | Cost | Latency |
|--------|----------|---------|------|---------|
| TransUnion | Large portfolio, fraud detection | KE, UG, TZ, ZA, ZM | Medium | 1-2s |
| Metropol | Kenya specialists, fast | KE only | Low | 0.5-1s |
| CRB Africa | Pan-African scale | 10+ African countries | Medium | 2-5s |
| Smile Identity | Digital ID specialists | 40+ African countries | Medium | 1-3s |
| Experian | Enterprise features | KE, ZA, expanding | High | 1-2s |

---

## Error Handling

The adapter raises specific exceptions for different error scenarios:

```python
from transunion_adapter import (
    TransUnionAdapterException,
    AuthenticationError,
    ConnectionError,
    APIError,
    ValidationError,
    TimeoutError
)

try:
    adapter.get_credit_report(...)
except AuthenticationError as e:
    # Handle auth failure (invalid credentials, token expiry)
    print(f"Auth failed: {e}")
except ValidationError as e:
    # Handle validation errors (missing fields, invalid format)
    print(f"Invalid input: {e}")
except TimeoutError as e:
    # Handle timeout (network delay, slow API)
    print(f"Timeout: {e}")
except APIError as e:
    # Handle API errors (rate limit, invalid request, server error)
    print(f"API error: {e}")
except ConnectionError as e:
    # Handle connection errors (unreachable, not connected)
    print(f"Connection error: {e}")
except TransUnionAdapterException as e:
    # Handle all other adapter errors
    print(f"Adapter error: {e}")
```

---

## Performance Optimization

### Connection Pooling

```python
# Reuse single adapter instance across requests
adapter = TransUnionAdapter(...)
adapter.connect()

# Process multiple queries with same connection
for customer in customers:
    report = adapter.get_credit_report(...)

adapter.disconnect()
```

### Batch Operations

For high-volume submissions:

```python
from concurrent.futures import ThreadPoolExecutor

def submit_loan(loan_data):
    return adapter.submit_loan_performance(**loan_data)

with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(submit_loan, loan_records))
```

### Caching

Implement caching layer for identical queries:

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def cached_credit_check(id_hash, first_name, last_name):
    # Only make API call if not cached
    return adapter.get_credit_score(...)

# Hash ID for privacy
id_hash = hashlib.sha256(id_number.encode()).hexdigest()
score = cached_credit_check(id_hash, first_name, last_name)
```

---

## Logging Configuration

```python
import logging

# Enable DEBUG logging for troubleshooting
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('transunion.log')
    ]
)

logger = logging.getLogger('TransUnionAdapter')
logger.setLevel(logging.DEBUG)

adapter = TransUnionAdapter(..., logger=logger)
```

---

## Testing

### Unit Tests

```python
import unittest
from unittest.mock import Mock, patch
from transunion_adapter import TransUnionAdapter

class TestTransUnionAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = TransUnionAdapter(
            auth_type="api_key",
            api_key="test_key",
            market="ke",
            environment="sandbox"
        )

    @patch('requests.Session.post')
    def test_authenticate(self, mock_post):
        # Mock OAuth token response
        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "test_token",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response

        self.adapter.connect()
        self.assertEqual(self.adapter.connection_state.value, "connected")

    @patch('requests.Session.request')
    def test_credit_report(self, mock_request):
        # Mock credit report response
        mock_response = Mock()
        mock_response.json.return_value = {
            "subject_id": "123",
            "score": {"score": 750, "rating": "Good"},
            "status": "active",
            "accounts_count": 3
        }
        mock_request.return_value = mock_response

        report = self.adapter.get_credit_report(
            id_type="national_id",
            id_number="12345678",
            first_name="John",
            last_name="Doe"
        )

        self.assertEqual(report.score.score, 750)
        self.assertEqual(report.status, "active")

if __name__ == '__main__':
    unittest.main()
```

### Integration Tests

```bash
# Test against sandbox environment
export TRANSUNION_ENVIRONMENT=sandbox
python -m pytest tests/integration/test_transunion_sandbox.py -v
```

---

## Production Checklist

- [ ] API credentials configured in environment variables
- [ ] SSL certificates installed and verified
- [ ] Firewall rules allow HTTPS to TransUnion endpoints
- [ ] Logging configured with rotation and retention
- [ ] Monitoring and alerting set up for IF.bus events
- [ ] Error handling tested for all failure scenarios
- [ ] Rate limiting implemented
- [ ] Data retention policy implemented
- [ ] Audit trails configured
- [ ] Security scan completed (credentials not hardcoded)
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] Rollback procedure documented
- [ ] Compliance review completed

---

## Troubleshooting

### Connection Failures

```python
# Debug connection issue
adapter.connect()
stats = adapter.get_stats()
print(f"Connection state: {stats['connection_state']}")
print(f"Last error: {stats['last_error']}")

# Check health
try:
    health = adapter.health_check()
    print(f"API health: {health}")
except Exception as e:
    print(f"API unreachable: {e}")
```

### Token Expiry Issues

```python
# Token automatically refreshes before expiry
# If manual refresh needed:
adapter._refresh_token_if_needed()
```

### Rate Limiting

The adapter automatically handles HTTP 429 (Too Many Requests) responses with exponential backoff. Check:

```python
stats = adapter.get_stats()
if stats['error_rate'] > 0.05:  # More than 5% errors
    print("High error rate detected, may be rate limited")
    time.sleep(60)  # Wait before retrying
```

### High Latency

Monitor response times:

```python
import time

start = time.time()
report = adapter.get_credit_report(...)
latency = time.time() - start
print(f"Request latency: {latency:.2f}s")
```

---

## Support & Documentation

- **InfraFabric Repository**: https://github.com/dannystocker/infrafabric
- **TransUnion API Docs**: Contact TransUnion support for regional API documentation
- **Issue Tracking**: Use InfraFabric GitHub issues for adapter improvements
- **Monitoring**: IF.bus events available at `redis://localhost:6379` (configurable)

---

## License

Part of InfraFabric project. See repository for license details.

---

**Last Updated**: 2025-12-04
**Maintainer**: InfraFabric FinTech Integration Team
