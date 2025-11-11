"""
SPDX-License-Identifier: MIT
Copyright (c) 2025 InfraFabric

Prometheus Metrics Exporter for SIP Escalate Proxy
--------------------------------------------------
Observability for IF.ESCALATE SIP proxy compliance audits.

Metrics:
- sip_calls_total: Counter of SIP calls by expert, hazard, and result
- sip_call_duration_seconds: Histogram of call durations
- sip_errors_total: Counter of SIP errors by status code
- sip_active_calls: Gauge of currently active calls
- sip_policy_decisions_total: Counter of IF.guard policy decisions
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CollectorRegistry
import time
from typing import Optional, Dict, Any
from datetime import datetime

# Create registry for SIP metrics
sip_registry = CollectorRegistry()

# Counter: Total SIP calls
sip_calls_total = Counter(
    'sip_calls_total',
    'Total SIP calls initiated',
    ['expert_id', 'hazard', 'result'],
    registry=sip_registry
)

# Histogram: Call duration in seconds
sip_call_duration_seconds = Histogram(
    'sip_call_duration_seconds',
    'SIP call duration in seconds',
    buckets=(0.1, 0.5, 1, 5, 10, 30, 60, 300, 600, 1800, 3600),
    registry=sip_registry
)

# Counter: SIP errors by status code
sip_errors_total = Counter(
    'sip_errors_total',
    'Total SIP errors by status code',
    ['status_code'],
    registry=sip_registry
)

# Gauge: Active SIP calls
sip_active_calls = Gauge(
    'sip_active_calls',
    'Currently active SIP calls',
    registry=sip_registry
)

# Counter: IF.guard policy decisions
sip_policy_decisions_total = Counter(
    'sip_policy_decisions_total',
    'IF.guard policy decisions (approved vs rejected)',
    ['result'],
    registry=sip_registry
)

# Histogram: IF.guard policy evaluation latency
sip_policy_eval_duration_seconds = Histogram(
    'sip_policy_eval_duration_seconds',
    'IF.guard policy evaluation latency in seconds',
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5),
    registry=sip_registry
)

# Counter: SIP responses by code
sip_responses_total = Counter(
    'sip_responses_total',
    'SIP responses by status code',
    ['status_code', 'status_type'],
    registry=sip_registry
)

# Histogram: SIP method latency
sip_method_duration_seconds = Histogram(
    'sip_method_duration_seconds',
    'SIP method execution latency',
    ['method'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1, 5),
    registry=sip_registry
)


class SIPMetricsCollector:
    """
    Collector for SIP proxy metrics

    Integrates with SIPEscalateProxy to record:
    - Call initiation and termination
    - Policy decisions
    - Error conditions
    - Performance metrics
    """

    def __init__(self):
        self.active_calls: Dict[str, Dict[str, Any]] = {}
        self.start_time = time.time()

    def record_call_initiated(self, call_id: str, expert_id: str, hazard: str) -> None:
        """
        Record call initiation

        Args:
            call_id: SIP call identifier
            expert_id: Expert SIP URI
            hazard: Hazard type
        """
        self.active_calls[call_id] = {
            'expert_id': expert_id,
            'hazard': hazard,
            'started_at': time.time()
        }
        sip_active_calls.set(len(self.active_calls))

    def record_call_terminated(
        self,
        call_id: str,
        result: str = "success"
    ) -> None:
        """
        Record call termination and duration

        Args:
            call_id: SIP call identifier
            result: "success" or "failed"
        """
        if call_id not in self.active_calls:
            return

        call_info = self.active_calls[call_id]
        duration = time.time() - call_info['started_at']

        # Record duration histogram
        sip_call_duration_seconds.observe(duration)

        # Record call total counter
        sip_calls_total.labels(
            expert_id=call_info['expert_id'],
            hazard=call_info['hazard'],
            result=result
        ).inc()

        # Remove from active calls
        del self.active_calls[call_id]
        sip_active_calls.set(len(self.active_calls))

    def record_policy_decision(
        self,
        result: str,
        eval_time: float = 0.0
    ) -> None:
        """
        Record IF.guard policy decision

        Args:
            result: "approved" or "rejected"
            eval_time: Policy evaluation time in seconds
        """
        sip_policy_decisions_total.labels(result=result).inc()

        if eval_time > 0:
            sip_policy_eval_duration_seconds.observe(eval_time)

    def record_sip_response(
        self,
        status_code: int,
        method: str = "INVITE"
    ) -> None:
        """
        Record SIP response

        Args:
            status_code: SIP response status code (e.g., 100, 180, 200, 403)
            method: SIP method name
        """
        # Determine status type
        if status_code < 200:
            status_type = "provisional"
        elif status_code < 300:
            status_type = "success"
        elif status_code < 400:
            status_type = "redirect"
        elif status_code < 500:
            status_type = "client_error"
        else:
            status_type = "server_error"

        sip_responses_total.labels(
            status_code=str(status_code),
            status_type=status_type
        ).inc()

        # Record errors
        if status_code >= 400:
            sip_errors_total.labels(status_code=str(status_code)).inc()

    def record_method_duration(self, method: str, duration: float) -> None:
        """
        Record SIP method execution duration

        Args:
            method: SIP method name (INVITE, BYE, ACK, etc.)
            duration: Execution time in seconds
        """
        sip_method_duration_seconds.labels(method=method).observe(duration)

    def record_error(self, status_code: int) -> None:
        """
        Record SIP error

        Args:
            status_code: Error status code
        """
        sip_errors_total.labels(status_code=str(status_code)).inc()

    def get_metrics(self) -> bytes:
        """
        Get all metrics in Prometheus format

        Returns:
            Prometheus exposition format bytes
        """
        return generate_latest(sip_registry)

    def get_active_call_count(self) -> int:
        """Get current active call count"""
        return len(self.active_calls)

    def get_uptime_seconds(self) -> float:
        """Get proxy uptime in seconds"""
        return time.time() - self.start_time


# Global metrics collector instance
_metrics_collector = SIPMetricsCollector()


def get_metrics_collector() -> SIPMetricsCollector:
    """Get global metrics collector instance"""
    return _metrics_collector


__all__ = [
    'SIPMetricsCollector',
    'get_metrics_collector',
    'sip_calls_total',
    'sip_call_duration_seconds',
    'sip_errors_total',
    'sip_active_calls',
    'sip_policy_decisions_total',
    'sip_policy_eval_duration_seconds',
    'sip_responses_total',
    'sip_method_duration_seconds',
]
