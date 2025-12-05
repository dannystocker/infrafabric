"""
Musoni Core Banking API Adapter

Thin adapter for Musoni Core Banking System, designed to be API-compatible
with Apache Fineract style endpoints (as commonly deployed with Musoni).

The goal is to provide a focused, easy-to-read implementation of the core
workflows needed for LOS/LMS style integrations:

- Client lifecycle (create, search, retrieve)
- Loan lifecycle (submit, approve, disburse, repay)
- Simple health checks and connection verification

This module intentionally mirrors the structure of the Mifos/Fineract adapter
while staying smaller and easier to extend for Musoni-specific behaviour.

Author: InfraFabric Finance Team
Status: Implementing
Version: 0.1.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

import requests
from requests.auth import HTTPBasicAuth

from fintech_debug_utils import ft_debug_log_request, ft_debug_log_response


class MusoniEnvironment(str, Enum):
    """Deployment environment. Used for logging/metrics only."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class MusoniAdapterError(Exception):
    """Base exception for Musoni adapter."""


class AuthenticationError(MusoniAdapterError):
    """Authentication/authorization failure."""


class ConnectionError(MusoniAdapterError):
    """Connection failure."""


class APIError(MusoniAdapterError):
    """HTTP/API error."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.response_body = response_body or {}
        super().__init__(message)


class ValidationError(MusoniAdapterError):
    """Invalid input before hitting the API."""


@dataclass
class MusoniClientData:
    """Minimal client data structure for Musoni/Fineract-compatible APIs."""

    first_name: str
    last_name: str
    office_id: int = 1
    middle_name: Optional[str] = None
    external_id: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[str] = None  # ISO yyyy-MM-dd
    gender: Optional[str] = None  # "m" / "f" or Musoni-specific values
    additional_fields: Dict[str, Any] = field(default_factory=dict)

    def to_api_dict(self) -> Dict[str, Any]:
        """Convert to Musoni/Fineract-style client payload."""
        payload: Dict[str, Any] = {
            "firstname": self.first_name,
            "lastname": self.last_name,
            "officeId": self.office_id,
        }
        if self.middle_name:
            payload["middlename"] = self.middle_name
        if self.external_id:
            payload["externalId"] = self.external_id
        if self.email:
            payload["email"] = self.email
        if self.phone_number:
            payload["mobileNo"] = self.phone_number
        if self.date_of_birth:
            payload["dateOfBirth"] = self.date_of_birth
        if self.gender:
            payload["gender"] = self.gender
        if self.additional_fields:
            payload.update(self.additional_fields)
        return payload


@dataclass
class MusoniLoanApplicationData:
    """Simplified loan application structure."""

    client_id: int
    product_id: int
    principal_amount: float
    number_of_repayments: int
    loan_term_frequency: int
    loan_term_frequency_type: int  # e.g. 2 = monthly in Fineract-style APIs
    interest_rate_per_period: float
    expected_disbursement_date: str  # ISO yyyy-MM-dd
    submitted_on_date: Optional[str] = None
    external_id: Optional[str] = None
    additional_fields: Dict[str, Any] = field(default_factory=dict)

    def to_api_dict(self) -> Dict[str, Any]:
        """Convert to Musoni/Fineract-style loan payload."""
        payload: Dict[str, Any] = {
            "clientId": self.client_id,
            "productId": self.product_id,
            "principal": self.principal_amount,
            "numberOfRepayments": self.number_of_repayments,
            "loanTermFrequency": self.loan_term_frequency,
            "loanTermFrequencyType": self.loan_term_frequency_type,
            "interestRatePerPeriod": self.interest_rate_per_period,
            "expectedDisbursementDate": self.expected_disbursement_date,
        }
        if self.submitted_on_date:
            payload["submittedOnDate"] = self.submitted_on_date
        if self.external_id:
            payload["externalId"] = self.external_id
        if self.additional_fields:
            payload.update(self.additional_fields)
        return payload


class MusoniAdapter:
    """
    Musoni Core Banking API adapter.

    This adapter assumes a Fineract-compatible Musoni deployment (Musoni often
    uses Fineract-style endpoints under the hood), so most URLs look like:

        {base_url}/api/v1/clients
        {base_url}/api/v1/loans

    If your deployment uses a different gateway or path prefix, supply the
    correct `base_url` (e.g. including `/musoni` or tenant prefix).

    The adapter focuses on a small, composable surface area; it can be extended
    with more endpoints as needed.
    """

    CLIENTS_ENDPOINT = "/api/v1/clients"
    LOANS_ENDPOINT = "/api/v1/loans"

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        tenant_id: Optional[str] = None,
        timeout: int = 30,
        verify_ssl: bool = True,
        environment: MusoniEnvironment = MusoniEnvironment.PRODUCTION,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        if not base_url or not username or not password:
            raise ValidationError("base_url, username and password are required")

        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.tenant_id = tenant_id
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.environment = environment

        self.logger = logger or logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(username, password)
        self.session.verify = verify_ssl

        self._last_connected: Optional[datetime] = None

    # --------------------------------------------------------------------- #
    # Internal helpers
    # --------------------------------------------------------------------- #

    def _build_url(self, path: str) -> str:
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = self._build_url(path)
        params = dict(params or {})

        # Musoni/Fineract deployments commonly use tenantIdentifier
        if self.tenant_id and "tenantIdentifier" not in params:
            params["tenantIdentifier"] = self.tenant_id

        try:
            ft_debug_log_request(
                self.logger,
                "musoni",
                url,
                {"method": method, "params": params or {}, "body": json or {}},
            )

            response = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise ConnectionError(f"Failed to connect to Musoni API: {exc}") from exc

        ft_debug_log_response(
            self.logger,
            "musoni",
            response.status_code,
            response.text,
        )

        if response.status_code == 401:
            raise AuthenticationError("Invalid Musoni API credentials")

        if not (200 <= response.status_code < 300):
            try:
                body = response.json()
            except ValueError:
                body = {"raw": response.text}
            raise APIError(
                f"Musoni API error {response.status_code}",
                status_code=response.status_code,
                response_body=body,
            )

        self._last_connected = datetime.utcnow()
        try:
            return response.json()
        except ValueError as exc:
            raise APIError("Musoni API returned non-JSON response") from exc

    # --------------------------------------------------------------------- #
    # Health / Info
    # --------------------------------------------------------------------- #

    def verify_connection(self) -> bool:
        """
        Verify that the Musoni API is reachable and credentials are valid.
        """
        # minimal call: list offices (Fineract-style)
        try:
            self._request("GET", "/api/v1/offices", params={"limit": 1})
            self.logger.info("Musoni connection verified")
            return True
        except MusoniAdapterError as exc:
            self.logger.error("Musoni connection failed: %s", exc)
            return False

    # --------------------------------------------------------------------- #
    # Client Operations
    # --------------------------------------------------------------------- #

    def create_client(self, client: MusoniClientData) -> Dict[str, Any]:
        """
        Create a new client in Musoni.

        Returns:
            Dictionary containing at least `client_id` / `resource_id`.
        """
        payload = client.to_api_dict()
        response = self._request("POST", self.CLIENTS_ENDPOINT, json=payload)
        client_id = response.get("resourceId") or response.get("clientId")
        return {
            "client_id": client_id,
            "resource_id": client_id,
            "raw": response,
        }

    def get_client(self, client_id: int) -> Dict[str, Any]:
        """
        Retrieve client details by ID.
        """
        return self._request("GET", f"{self.CLIENTS_ENDPOINT}/{client_id}")

    # --------------------------------------------------------------------- #
    # Loan Operations
    # --------------------------------------------------------------------- #

    def submit_loan_application(
        self,
        loan: MusoniLoanApplicationData,
    ) -> Dict[str, Any]:
        """
        Submit a new loan application for a client.
        """
        payload = loan.to_api_dict()
        response = self._request("POST", self.LOANS_ENDPOINT, json=payload)
        loan_id = response.get("resourceId") or response.get("loanId")
        return {
            "loan_id": loan_id,
            "resource_id": loan_id,
            "raw": response,
        }

    def approve_loan(self, loan_id: int, note: str = "", approved_on_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Approve a pending loan.
        """
        payload: Dict[str, Any] = {"note": note}
        if approved_on_date:
            payload["approvedOnDate"] = approved_on_date

        return self._request(
            "POST",
            f"{self.LOANS_ENDPOINT}/{loan_id}",
            params={"command": "approve"},
            json=payload,
        )

    def disburse_loan(
        self,
        loan_id: int,
        transaction_amount: float,
        actual_disbursement_date: str,
        external_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Disburse an approved loan.
        """
        payload: Dict[str, Any] = {
            "transactionAmount": transaction_amount,
            "actualDisbursementDate": actual_disbursement_date,
        }
        if external_id:
            payload["externalId"] = external_id

        return self._request(
            "POST",
            f"{self.LOANS_ENDPOINT}/{loan_id}",
            params={"command": "disburse"},
            json=payload,
        )

    def post_repayment(
        self,
        loan_id: int,
        transaction_amount: float,
        transaction_date: str,
        external_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Post a repayment transaction against a loan.
        """
        payload: Dict[str, Any] = {
            "transactionAmount": transaction_amount,
            "transactionDate": transaction_date,
        }
        if external_id:
            payload["externalId"] = external_id

        return self._request(
            "POST",
            f"{self.LOANS_ENDPOINT}/{loan_id}/transactions",
            json=payload,
        )
