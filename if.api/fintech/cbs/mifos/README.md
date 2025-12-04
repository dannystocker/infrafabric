# Apache Fineract/Mifos API Adapter

Production-ready Python adapter for Apache Fineract/Mifos Core Banking System integration with InfraFabric platform.

**Version:** 1.0.0
**Status:** Production Ready
**API Compatibility:** Fineract 1.0.0 - 1.4.x
**Citation:** `if://adapter/fintech/mifos-cbs/v1`

---

## Overview

This adapter provides complete integration with Apache Fineract (Mifos) for microfinance institution (MFI) operations. It implements the full client and loan lifecycle, savings accounts, and group lending models with IF.TTT compliance (Traceable, Transparent, Trustworthy).

### Supported Features

- **Client Management**: Create, search, retrieve, update, activate clients
- **Loan Products**: Query available products with parameters
- **Loan Lifecycle**: Submit applications, approve, disburse, post repayments
- **Loan Schedules**: Retrieve repayment schedules and transactions
- **Savings Accounts**: Create, activate, manage savings products
- **Group Lending**: Center and group management for MFI collective models
- **Group Membership**: Add/remove clients from groups
- **IF.bus Integration**: Event emission for system-wide workflow coordination
- **Error Handling**: Comprehensive exception hierarchy with context preservation
- **Pagination**: Built-in support for large result sets
- **Connection Pooling**: Efficient HTTP session management

---

## Installation & Setup

### 1. System Requirements

```bash
# Required Python version
python >= 3.8

# Required packages (via pip or requirements.txt)
requests >= 2.25.0
```

### 2. Environment Configuration

Create a `.env` file in your project root or set environment variables:

```bash
# Fineract Server Configuration
FINERACT_URL=https://fineract.example.com
FINERACT_USERNAME=admin
FINERACT_PASSWORD=your_secure_password

# Optional: Deployment environment
FINERACT_ENVIRONMENT=production  # Options: development, staging, production

# Optional: Connection settings
FINERACT_TIMEOUT=30
FINERACT_VERIFY_SSL=true
```

### 3. Import the Adapter

```python
from mifos_adapter import (
    MifosAdapter,
    ClientData,
    LoanApplicationData,
    RepaymentData,
    SavingsAccountData,
    GroupData,
    PaginationParams,
    MifosEnvironment,
)
```

---

## Quick Start

### Basic Connection

```python
import os
from mifos_adapter import MifosAdapter

# Initialize adapter
adapter = MifosAdapter(
    base_url=os.getenv("FINERACT_URL"),
    username=os.getenv("FINERACT_USERNAME"),
    password=os.getenv("FINERACT_PASSWORD"),
    environment=MifosEnvironment.PRODUCTION
)

# Verify connection
if adapter.verify_connection():
    print("Connected to Fineract!")
    info = adapter.get_server_info()
    print(f"Fineract version: {info.get('version')}")
```

### Using Context Manager (Recommended)

```python
with MifosAdapter(
    base_url="https://fineract.example.com",
    username="admin",
    password="password"
) as adapter:
    # Your operations here
    clients = adapter.search_clients(search_term="Jane")
    for client in clients["pageItems"]:
        print(f"{client['displayName']}")
```

---

## Common Workflows

### 1. Create and Activate a Client

```python
from mifos_adapter import MifosAdapter, ClientData

adapter = MifosAdapter(
    base_url="https://fineract.example.com",
    username="admin",
    password="password"
)

# Create client
client = ClientData(
    first_name="Jane",
    last_name="Kipchoge",
    external_id="KE-JAK-20251204-001",
    email="jane@example.com",
    phone_number="+254712345678",
    date_of_birth="1990-05-15",
    gender="f",
    national_id="KE123456789"
)

result = adapter.create_client(client)
client_id = result["client_id"]
print(f"Client created with ID: {client_id}")

# Activate client (change status from PENDING to ACTIVE)
activation_result = adapter.activate_client(client_id)
print(f"Client activated: {activation_result}")
```

### 2. Search Clients

```python
from mifos_adapter import PaginationParams

# Search by name
results = adapter.search_clients(
    search_term="Jane",
    pagination=PaginationParams(offset=0, limit=50)
)

print(f"Found {results['totalFilteredRecords']} clients")
for client in results["pageItems"]:
    print(f"  - {client['id']}: {client['displayName']}")

# Search by external ID
results = adapter.search_clients(external_id="KE-JAK-20251204-001")
```

### 3. Submit and Manage Loan Application

```python
from mifos_adapter import LoanApplicationData, RepaymentData
from datetime import datetime, timedelta

# Check available products
products = adapter.get_loan_products()
product_id = products["pageItems"][0]["id"]

# Submit loan application
loan = LoanApplicationData(
    client_id=123,
    product_id=product_id,
    principal_amount=50000.0,
    number_of_repayments=24,
    repayment_every=1,
    repayment_frequency_id=2,  # Monthly
    interest_rate_per_period=2.5,
    interest_type=0,  # Flat interest
    submission_on_date=datetime.utcnow().strftime("%Y-%m-%d"),
    expected_disbursement_date=(datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d"),
    external_id="LN-JAK-001"
)

submission_result = adapter.submit_loan_application(loan)
loan_id = submission_result["loan_id"]
print(f"Loan application submitted: {loan_id}")

# Approve loan
approval_result = adapter.approve_loan(
    loan_id=loan_id,
    approval_date=datetime.utcnow().strftime("%Y-%m-%d"),
    approval_amount=50000.0
)
print(f"Loan approved: {approval_result}")

# Disburse loan
disbursal_result = adapter.disburse_loan(
    loan_id=loan_id,
    disbursal_date=(datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d"),
    disbursal_amount=50000.0
)
print(f"Loan disbursed: {disbursal_result}")

# Get loan details
loan_details = adapter.get_loan(loan_id)
print(f"Loan status: {loan_details['status']}")
print(f"Outstanding balance: {loan_details['summary']['principalOutstanding']}")

# Get repayment schedule
schedule = adapter.get_loan_schedule(loan_id)
for period in schedule["periods"]:
    print(f"Period {period['period']}: {period['dueDate']} - {period['totalDueForPeriod']}")

# Post repayment
repayment = RepaymentData(
    loan_id=loan_id,
    transaction_date=datetime.utcnow().strftime("%Y-%m-%d"),
    amount=5000.0,
    receipt_number="RCP-20251204-001"
)

repayment_result = adapter.post_loan_repayment(repayment)
print(f"Repayment posted: {repayment_result}")
```

### 4. Manage Savings Accounts

```python
from mifos_adapter import SavingsAccountData

# Create savings account
savings = SavingsAccountData(
    client_id=123,
    product_id=2,
    nominal_annual_interest_rate=2.5,
    submission_on_date=datetime.utcnow().strftime("%Y-%m-%d")
)

savings_result = adapter.create_savings_account(savings)
account_id = savings_result["savings_account_id"]
print(f"Savings account created: {account_id}")

# Activate savings account
activation = adapter.activate_savings_account(
    account_id=account_id,
    activation_date=datetime.utcnow().strftime("%Y-%m-%d")
)

# Get account details
account = adapter.get_savings_account(account_id)
print(f"Account balance: {account['summary']['accountBalance']}")
```

### 5. Group Lending (MFI Collections Model)

```python
from mifos_adapter import GroupData, GroupType

# Create a center (umbrella for multiple groups)
center = GroupData(
    group_name="Nairobi Center 1",
    office_id=1,
    group_type=GroupType.CENTER,
    activation_date=datetime.utcnow().strftime("%Y-%m-%d")
)

center_result = adapter.create_group(center)
center_id = center_result["group_id"]
print(f"Center created: {center_id}")

# Create a self-help group within the center
group = GroupData(
    group_name="Jamii Self Help Group",
    office_id=1,
    center_id=center_id,
    group_type=GroupType.SELF_HELP_GROUP,
    activation_date=datetime.utcnow().strftime("%Y-%m-%d")
)

group_result = adapter.create_group(group)
group_id = group_result["group_id"]
print(f"Group created: {group_id}")

# Add clients to group
adapter.add_client_to_group(group_id, 123)
adapter.add_client_to_group(group_id, 124)

# Get group details
group_details = adapter.get_group(group_id)
print(f"Group members: {len(group_details.get('clientMembers', []))}")
```

---

## IF.bus Integration

The adapter emits standardized events for system-wide coordination using IF.bus (InfraFabric event bus).

### Supported Events

```
# Client Events
fintech.client.created      - New client created
fintech.client.updated      - Client information updated
fintech.client.activated    - Client status changed to ACTIVE
fintech.client.searched     - Client search performed

# Loan Events
fintech.loan.submitted      - Loan application submitted
fintech.loan.approved       - Loan approved by system
fintech.loan.disbursed      - Loan funds disbursed
fintech.loan.repaid         - Loan repayment posted

# Savings Events
fintech.savings.created     - Savings account created
fintech.savings.activated   - Savings account activated

# Group Events
fintech.group.created       - Group/center created
fintech.group.member_added  - Client added to group
```

### Custom Event Emitter Implementation

```python
from mifos_adapter import MifosAdapter, EventEmitter, MifosEvent
import redis
import json

class RedisEventEmitter(EventEmitter):
    """Emit events to Redis Pub/Sub for IF.bus integration."""

    def __init__(self, redis_url="redis://localhost:6379"):
        self.redis = redis.from_url(redis_url)

    def emit(self, event: MifosEvent) -> None:
        """Publish event to Redis channel."""
        channel = f"if.bus:fintech:{event.entity_type}"
        payload = json.dumps(event.to_dict())
        self.redis.publish(channel, payload)
        print(f"Event emitted to {channel}")

# Use custom emitter
emitter = RedisEventEmitter()
adapter = MifosAdapter(
    base_url="https://fineract.example.com",
    username="admin",
    password="password",
    event_emitter=emitter
)

# Now all operations automatically emit events
result = adapter.create_client(client_data)
# Automatically publishes: if.bus:fintech:client
```

---

## Error Handling

The adapter provides a comprehensive exception hierarchy:

```python
from mifos_adapter import (
    MifosAdapterError,
    AuthenticationError,
    ConnectionError,
    ValidationError,
    APIError,
    ResourceNotFoundError,
    ConflictError
)

try:
    adapter.get_client(999)
except ResourceNotFoundError as e:
    print(f"Client not found: {e.message}")
    print(f"Request ID: {e.request_id}")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except APIError as e:
    print(f"API error {e.status_code}: {e.message}")
    print(f"Response: {e.response_body}")
except MifosAdapterError as e:
    print(f"Adapter error: {e}")
```

### Example: Handling Loan Approval Conflicts

```python
try:
    adapter.approve_loan(loan_id=123)
except ConflictError as e:
    if "already approved" in e.message:
        print("Loan already approved")
    elif "invalid status" in e.message:
        print("Loan in invalid state for approval")
    else:
        raise
```

---

## Pagination for Large Result Sets

Use `PaginationParams` for efficient handling of large result sets:

```python
from mifos_adapter import PaginationParams

# Paginate through all clients
pagination = PaginationParams(
    offset=0,
    limit=100,
    sort_by="displayName",
    sort_order="ASC"
)

while True:
    results = adapter.search_clients(pagination=pagination)

    for client in results["pageItems"]:
        print(f"{client['displayName']}")

    # Check if more pages exist
    if len(results["pageItems"]) < pagination.limit:
        break

    # Move to next page
    pagination.offset += pagination.limit
```

---

## Advanced Configuration

### Timeout and SSL Settings

```python
adapter = MifosAdapter(
    base_url="https://fineract.example.com",
    username="admin",
    password="password",
    timeout=60,  # 60 second timeout
    verify_ssl=True,  # Verify SSL certificates
    environment=MifosEnvironment.DEVELOPMENT
)
```

### Logging

```python
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("mifos_adapter")
logger.setLevel(logging.DEBUG)

adapter = MifosAdapter(
    base_url="https://fineract.example.com",
    username="admin",
    password="password",
    logger=logger
)
```

---

## Migration Notes for Musoni Users

Musoni is a specialized fork of Fineract designed for microfinance. The Mifos adapter is compatible with Musoni instances since they share the Fineract API.

### Compatibility

```
Musoni Version    -> Fineract Equivalent
1.0.x - 1.3.x     -> Fineract 1.x compatible
```

### Differences to Note

1. **API Endpoint Base Path**: Verify your Musoni instance uses `/api/v1` endpoints
2. **Authentication**: Musoni uses same HTTPBasicAuth as Fineract
3. **Custom Fields**: Musoni may have additional custom fields beyond standard Fineract
4. **Product Types**: Verify loan product configurations match your setup

### Example: Musoni Connection

```python
adapter = MifosAdapter(
    base_url="https://musoni.yourbank.com",  # Musoni instance
    username="admin",
    password="password"
)

# Verify Musoni compatibility
info = adapter.get_server_info()
print(f"Server: {info.get('name')}")
```

---

## API Version Compatibility

### Supported Fineract Versions

| Version | Status | Notes |
|---------|--------|-------|
| 1.0.0   | Supported | Base version, all features |
| 1.1.x   | Supported | Group lending enhancements |
| 1.2.x   | Supported | Batch processing additions |
| 1.3.x   | Supported | Improved error handling |
| 1.4.x   | Supported | Latest stable release |
| 2.0.0+  | Not Yet Supported | Different API structure (future) |

### Feature Availability by Version

| Feature | 1.0.0+ | Notes |
|---------|--------|-------|
| Basic Clients | Yes | All versions |
| Loans | Yes | Core functionality |
| Savings | Yes | Supported throughout |
| Groups | 1.1.0+ | Group lending added in 1.1 |
| Centers | 1.1.0+ | Center hierarchy in 1.1+ |
| Batch Operations | 1.2.0+ | Available from 1.2 |

---

## Type Hints and IDE Support

All methods include comprehensive type hints for full IDE autocomplete:

```python
def submit_loan_application(
    self,
    loan_data: LoanApplicationData,
    emit_event: bool = True
) -> Dict[str, Any]:
    """Full docstring with examples..."""
    pass
```

This enables:
- Autocomplete in VSCode, PyCharm, etc.
- Type checking with mypy/pyright
- Inline documentation hover

---

## Performance Optimization

### Connection Pooling

The adapter uses HTTP session pooling for efficiency:

```python
# Session is reused across requests - efficient for bulk operations
for i in range(100):
    adapter.create_client(client_data)  # Reuses same connection
```

### Batch Operations

For creating many entities, keep adapter open:

```python
with MifosAdapter(...) as adapter:
    for client_dict in large_client_list:
        client = ClientData(**client_dict)
        adapter.create_client(client)
```

---

## Testing

### Unit Test Example

```python
import pytest
from unittest.mock import Mock, patch
from mifos_adapter import MifosAdapter, ClientData

def test_create_client():
    """Test client creation."""
    with patch("requests.Session.request") as mock_request:
        # Mock Fineract response
        mock_request.return_value.status_code = 201
        mock_request.return_value.json.return_value = {
            "resourceId": 123,
            "resourceIdentifier": "123"
        }

        adapter = MifosAdapter(
            base_url="http://localhost:8080",
            username="admin",
            password="password"
        )

        client = ClientData(
            first_name="Jane",
            last_name="Doe"
        )

        result = adapter.create_client(client)
        assert result["client_id"] == 123
```

---

## Troubleshooting

### Connection Issues

```python
# Error: "Failed to connect to Fineract"
# Solution: Verify URL and network connectivity
adapter.verify_connection()  # Returns True if OK

# Check server info
info = adapter.get_server_info()
```

### Authentication Errors

```python
# Error: "Authentication failed"
# Verify credentials
# Check if user has API access permissions
# Verify username/password are correct
```

### Validation Errors

```python
# Error: "first_name and last_name are required"
client = ClientData(
    first_name="Valid",  # Must not be empty
    last_name="Name"     # Must not be empty
)
```

### API Errors with Response Details

```python
try:
    adapter.get_client(999)
except APIError as e:
    print(f"Status: {e.status_code}")
    print(f"Message: {e.message}")
    print(f"Details: {e.response_body}")
    print(f"Request ID: {e.request_id}")
```

---

## License & Citation

**Citation Format:**
```
if://adapter/fintech/mifos-cbs/v1
```

**Author:** InfraFabric Platform
**Version:** 1.0.0
**Last Updated:** 2025-12-04
**Status:** Production Ready

---

## Support & Contributing

For issues, questions, or contributions:

1. Check existing documentation in `/home/setup/infrafabric/`
2. Review IF.TTT compliance principles
3. Follow IF.bus event emission patterns
4. Maintain backward compatibility with Fineract 1.x

### Key Principles

- **IF.TTT Compliance**: All operations are Traceable, Transparent, Trustworthy
- **Event Emission**: All major state changes emit IF.bus events
- **Error Context**: Errors preserve full request context for debugging
- **Type Safety**: Full type hints throughout codebase

---

## Related Resources

- Apache Fineract: https://fineract.apache.org/
- Fineract API Documentation: https://fineract.apache.org/docs/apiLive.htm
- Musoni: https://www.musoni.com/
- InfraFabric: `/home/setup/infrafabric/`
- IF.story Protocol: `/home/setup/infrafabric/prompts/IF.story.md`
