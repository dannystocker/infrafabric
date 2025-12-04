"""
Airtel Money Adapter - Integration Tests

Test suite for Airtel Money adapter integration.
Run these tests in sandbox environment before production deployment.

Usage:
    python test_integration.py

Requirements:
    - Set AIRTEL_CLIENT_ID and AIRTEL_CLIENT_SECRET environment variables
    - Use sandbox credentials for testing

Author: InfraFabric Finance Team
Version: 1.0.0
Date: 2025-12-04
"""

import os
import sys
import logging
import time
from typing import Dict, Any, List

from airtel_money_adapter import (
    AirtelMoneyAdapter,
    CountryCode,
    TransactionStatus,
    AirtelMoneyError,
    AuthenticationError,
    APIError,
    ValidationError,
)
from config import (
    get_country_config,
    validate_phone_number,
    validate_amount,
    list_supported_countries,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class TestResult:
    """Test result tracker."""

    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.error = None
        self.duration = 0.0

    def __repr__(self) -> str:
        status = "✓ PASS" if self.passed else "✗ FAIL"
        error_msg = f" - {self.error}" if self.error else ""
        return f"{status} [{self.duration:.2f}s] {self.name}{error_msg}"


class AirtelMoneyIntegrationTests:
    """Integration test suite for Airtel Money adapter."""

    def __init__(self, use_sandbox: bool = True):
        """
        Initialize test suite.

        Args:
            use_sandbox: Use sandbox environment for testing
        """
        self.use_sandbox = use_sandbox
        self.results: List[TestResult] = []
        self.adapter = None

    def setup(self) -> bool:
        """
        Setup test environment.

        Returns:
            True if setup successful
        """
        logger.info("Setting up test environment...")

        # Check for credentials
        client_id = os.getenv("AIRTEL_CLIENT_ID")
        client_secret = os.getenv("AIRTEL_CLIENT_SECRET")

        if not client_id or not client_secret:
            logger.error("AIRTEL_CLIENT_ID and AIRTEL_CLIENT_SECRET must be set")
            return False

        # Initialize adapter
        try:
            self.adapter = AirtelMoneyAdapter(
                client_id=client_id,
                client_secret=client_secret,
                country=CountryCode.KENYA,
                environment="sandbox" if self.use_sandbox else "production",
                pin=os.getenv("AIRTEL_PIN", "1234"),
            )
            logger.info(f"✓ Adapter initialized (sandbox={self.use_sandbox})")
            return True

        except Exception as e:
            logger.error(f"✗ Adapter initialization failed: {e}")
            return False

    def teardown(self):
        """Cleanup test environment."""
        if self.adapter:
            self.adapter.close()
            logger.info("✓ Adapter closed")

    def run_test(self, test_func, name: str) -> TestResult:
        """
        Run a single test.

        Args:
            test_func: Test function to run
            name: Test name

        Returns:
            TestResult instance
        """
        result = TestResult(name)
        start_time = time.time()

        try:
            logger.info(f"\nRunning: {name}")
            test_func()
            result.passed = True
            logger.info(f"✓ {name} passed")

        except AssertionError as e:
            result.error = f"Assertion failed: {e}"
            logger.error(f"✗ {name} failed: {e}")

        except Exception as e:
            result.error = f"Exception: {e}"
            logger.error(f"✗ {name} error: {e}")

        finally:
            result.duration = time.time() - start_time

        self.results.append(result)
        return result

    # ========================================================================
    # Configuration Tests
    # ========================================================================

    def test_country_config(self):
        """Test country configuration retrieval."""
        country = get_country_config("KE")
        assert country is not None, "Kenya config should exist"
        assert country.currency == "KES", f"Expected KES, got {country.currency}"
        assert country.phone_prefix == "254", f"Expected 254, got {country.phone_prefix}"
        logger.info(f"  Kenya config: {country.currency}, +{country.phone_prefix}")

    def test_list_countries(self):
        """Test listing all supported countries."""
        countries = list_supported_countries()
        assert len(countries) == 14, f"Expected 14 countries, got {len(countries)}"
        logger.info(f"  Supported countries: {len(countries)}")

    def test_phone_validation(self):
        """Test phone number validation."""
        # Valid phone
        valid, error = validate_phone_number("254712345678", "KE")
        assert valid, f"Valid phone should pass: {error}"

        # Invalid phone (wrong length)
        valid, error = validate_phone_number("25471234567", "KE")
        assert not valid, "Invalid phone should fail"
        logger.info(f"  Phone validation working correctly")

    def test_amount_validation(self):
        """Test amount validation."""
        # Valid amount
        valid, error = validate_amount(1000.0, "collection", "KE")
        assert valid, f"Valid amount should pass: {error}"

        # Invalid amount (negative)
        valid, error = validate_amount(-100.0, "collection", "KE")
        assert not valid, "Negative amount should fail"
        logger.info(f"  Amount validation working correctly")

    # ========================================================================
    # Authentication Tests
    # ========================================================================

    def test_authentication(self):
        """Test OAuth2 authentication."""
        # Get access token
        token = self.adapter._get_access_token()
        assert token is not None, "Access token should be returned"
        assert len(token) > 0, "Access token should not be empty"
        logger.info(f"  Token obtained: {token[:20]}...")

    def test_token_caching(self):
        """Test token caching."""
        # First call
        token1 = self.adapter._get_access_token()

        # Second call (should use cached token)
        token2 = self.adapter._get_access_token()

        assert token1 == token2, "Cached token should be the same"
        logger.info(f"  Token caching working correctly")

    # ========================================================================
    # Account API Tests
    # ========================================================================

    def test_get_balance(self):
        """Test balance inquiry."""
        balance = self.adapter.get_balance()

        assert "balance" in balance, "Balance should contain 'balance' key"
        assert "currency" in balance, "Balance should contain 'currency' key"
        assert isinstance(balance["balance"], (int, float)), "Balance should be numeric"

        logger.info(f"  Balance: {balance['balance']} {balance['currency']}")

    # ========================================================================
    # KYC API Tests
    # ========================================================================

    def test_kyc_inquiry(self):
        """Test KYC inquiry."""
        # Use test phone number
        test_phone = "254712345678"

        try:
            kyc = self.adapter.kyc_inquiry(test_phone)

            assert kyc is not None, "KYC result should not be None"
            assert kyc.msisdn == test_phone, f"Expected {test_phone}, got {kyc.msisdn}"

            logger.info(f"  KYC inquiry completed: Verified={kyc.is_verified}")

            if kyc.is_verified:
                logger.info(f"  Customer: {kyc.full_name}")
                logger.info(f"  ID: {kyc.id_number}")

        except APIError as e:
            # KYC inquiry may fail in sandbox
            logger.warning(f"  KYC inquiry failed (expected in sandbox): {e}")

    # ========================================================================
    # Collections API Tests
    # ========================================================================

    def test_ussd_push(self):
        """Test USSD Push collection."""
        test_phone = "254712345678"
        test_amount = 100.0

        try:
            result = self.adapter.ussd_push(
                amount=test_amount,
                msisdn=test_phone,
                reference=f"TEST-COLL-{int(time.time())}",
                description="Test collection",
            )

            assert "transaction_id" in result, "Result should contain transaction_id"
            assert "reference" in result, "Result should contain reference"
            assert "status" in result, "Result should contain status"

            logger.info(f"  USSD Push initiated: {result['transaction_id']}")
            logger.info(f"  Status: {result['status']}")

        except APIError as e:
            # USSD Push may fail in sandbox
            logger.warning(f"  USSD Push failed (expected in sandbox): {e}")

    def test_collection_status(self):
        """Test collection status check."""
        # First create a collection
        test_phone = "254712345678"

        try:
            result = self.adapter.ussd_push(
                amount=100.0,
                msisdn=test_phone,
                reference=f"TEST-STATUS-{int(time.time())}",
                description="Test status check",
            )

            transaction_id = result["transaction_id"]

            # Wait a bit
            time.sleep(2)

            # Check status
            status = self.adapter.get_collection_status(transaction_id)

            assert "transaction_id" in status, "Status should contain transaction_id"
            assert "status" in status, "Status should contain status"

            logger.info(f"  Status check completed: {status['status']}")

        except APIError as e:
            logger.warning(f"  Status check failed (expected in sandbox): {e}")

    # ========================================================================
    # Validation Tests
    # ========================================================================

    def test_invalid_amount(self):
        """Test invalid amount handling."""
        try:
            self.adapter.ussd_push(
                amount=-100.0,  # Invalid negative amount
                msisdn="254712345678",
                reference="TEST-INVALID",
                description="Test",
            )
            raise AssertionError("Should have raised ValidationError")

        except ValidationError as e:
            logger.info(f"  Correctly rejected invalid amount: {e}")

    def test_invalid_phone(self):
        """Test invalid phone number handling."""
        try:
            self.adapter.ussd_push(
                amount=100.0,
                msisdn="",  # Invalid empty phone
                reference="TEST-INVALID",
                description="Test",
            )
            raise AssertionError("Should have raised ValidationError")

        except ValidationError as e:
            logger.info(f"  Correctly rejected invalid phone: {e}")

    # ========================================================================
    # Run All Tests
    # ========================================================================

    def run_all(self) -> Dict[str, Any]:
        """
        Run all integration tests.

        Returns:
            Test summary dictionary
        """
        logger.info("=" * 80)
        logger.info("AIRTEL MONEY INTEGRATION TESTS")
        logger.info("=" * 80)

        # Setup
        if not self.setup():
            logger.error("Setup failed - cannot run tests")
            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "success_rate": 0.0,
            }

        # Configuration tests
        logger.info("\n--- Configuration Tests ---")
        self.run_test(self.test_country_config, "Country Configuration")
        self.run_test(self.test_list_countries, "List Countries")
        self.run_test(self.test_phone_validation, "Phone Validation")
        self.run_test(self.test_amount_validation, "Amount Validation")

        # Authentication tests
        logger.info("\n--- Authentication Tests ---")
        self.run_test(self.test_authentication, "OAuth2 Authentication")
        self.run_test(self.test_token_caching, "Token Caching")

        # Account tests
        logger.info("\n--- Account API Tests ---")
        self.run_test(self.test_get_balance, "Get Balance")

        # KYC tests
        logger.info("\n--- KYC API Tests ---")
        self.run_test(self.test_kyc_inquiry, "KYC Inquiry")

        # Collections tests
        logger.info("\n--- Collections API Tests ---")
        self.run_test(self.test_ussd_push, "USSD Push")
        self.run_test(self.test_collection_status, "Collection Status")

        # Validation tests
        logger.info("\n--- Validation Tests ---")
        self.run_test(self.test_invalid_amount, "Invalid Amount")
        self.run_test(self.test_invalid_phone, "Invalid Phone")

        # Teardown
        self.teardown()

        # Summary
        total = len(self.results)
        passed = len([r for r in self.results if r.passed])
        failed = total - passed
        success_rate = (passed / total * 100) if total > 0 else 0

        logger.info("\n" + "=" * 80)
        logger.info("TEST SUMMARY")
        logger.info("=" * 80)

        for result in self.results:
            logger.info(result)

        logger.info("\n" + "-" * 80)
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info("-" * 80)

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "success_rate": success_rate,
            "results": self.results,
        }


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Run integration tests."""
    # Check for credentials
    if not os.getenv("AIRTEL_CLIENT_ID") or not os.getenv("AIRTEL_CLIENT_SECRET"):
        print("\n⚠ ERROR: AIRTEL_CLIENT_ID and AIRTEL_CLIENT_SECRET must be set")
        print("\nSet environment variables:")
        print("  export AIRTEL_CLIENT_ID=your-client-id")
        print("  export AIRTEL_CLIENT_SECRET=your-client-secret")
        print("\nUse sandbox credentials for testing")
        sys.exit(1)

    # Run tests
    tests = AirtelMoneyIntegrationTests(use_sandbox=True)
    summary = tests.run_all()

    # Exit with appropriate code
    if summary["success_rate"] < 100:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
