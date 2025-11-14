"""
Event processor - normalizes and enriches events.
"""
import re
from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

from models import AIEvent, RiskLevel


class EventProcessor:
    """Process and enrich AI events."""

    def __init__(self):
        self.pii_patterns = self._compile_pii_patterns()
        self.injection_patterns = self._compile_injection_patterns()

    def _compile_pii_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for PII detection."""
        return {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            'credit_card': re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
            'ip_address': re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
        }

    def _compile_injection_patterns(self) -> List[re.Pattern]:
        """Compile regex patterns for injection detection."""
        patterns = [
            r'ignore\s+previous\s+instructions',
            r'disregard\s+all\s+prior',
            r'new\s+instructions:',
            r'system\s*:\s*you\s+are',
            r'</prompt>.*<prompt>',
            r'\\n\\nHuman:',
            r'\\n\\nAssistant:',
        ]
        return [re.compile(p, re.IGNORECASE) for p in patterns]

    def process_event(self, event: AIEvent) -> AIEvent:
        """
        Process and enrich an event.

        Adds:
        - PII detection
        - Injection attempt detection
        - Risk level calculation
        """
        # Check for PII
        if event.prompt:
            event.has_pii = self._detect_pii(event.prompt)

        if event.response:
            event.has_pii = event.has_pii or self._detect_pii(event.response)

        # Check for injection attempts
        if event.prompt:
            event.injection_detected = self._detect_injection(event.prompt)

        # Calculate risk level
        event.risk_level = self._calculate_risk_level(event)

        return event

    def _detect_pii(self, text: str) -> bool:
        """Detect PII in text."""
        for pattern_type, pattern in self.pii_patterns.items():
            if pattern.search(text):
                return True
        return False

    def _detect_injection(self, text: str) -> bool:
        """Detect prompt injection attempts."""
        for pattern in self.injection_patterns:
            if pattern.search(text):
                return True
        return False

    def _calculate_risk_level(self, event: AIEvent) -> RiskLevel:
        """Calculate risk level for an event."""
        risk_score = 0

        # Failed requests are risky
        if not event.success:
            risk_score += 3

        # Injection attempts are very risky
        if event.injection_detected:
            risk_score += 4

        # PII is moderately risky
        if event.has_pii:
            risk_score += 2

        # High latency might indicate issues
        if event.latency_ms and event.latency_ms > 10000:  # 10 seconds
            risk_score += 1

        # High token usage might indicate issues
        if event.tokens and event.tokens.total_tokens > 10000:
            risk_score += 1

        # High cost
        if event.cost_usd > 1.0:  # More than $1 per request
            risk_score += 2

        # Map score to risk level
        if risk_score >= 5:
            return RiskLevel.CRITICAL
        elif risk_score >= 3:
            return RiskLevel.HIGH
        elif risk_score >= 1:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW


class EventAggregator:
    """Aggregate events for metrics."""

    def __init__(self):
        self.events: List[AIEvent] = []

    def add_event(self, event: AIEvent):
        """Add event to aggregator."""
        self.events.append(event)

    def get_metrics(self, window_minutes: int = 60) -> Dict[str, Any]:
        """Get aggregated metrics for a time window."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent_events = [e for e in self.events if e.timestamp >= cutoff_time]

        if not recent_events:
            return {
                'total_requests': 0,
                'time_window_minutes': window_minutes
            }

        # Basic metrics
        total = len(recent_events)
        successful = sum(1 for e in recent_events if e.success)
        failed = total - successful

        # Token metrics
        total_tokens = sum(e.tokens.total_tokens for e in recent_events if e.tokens)

        # Latency metrics
        latencies = [e.latency_ms for e in recent_events if e.latency_ms is not None]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        max_latency = max(latencies) if latencies else 0

        # Cost metrics
        total_cost = sum(e.cost_usd for e in recent_events)

        # Security metrics
        pii_detected = sum(1 for e in recent_events if e.has_pii)
        injections_detected = sum(1 for e in recent_events if e.injection_detected)

        # By provider
        by_provider = defaultdict(int)
        for e in recent_events:
            by_provider[e.provider.value] += 1

        # By model
        by_model = defaultdict(int)
        for e in recent_events:
            by_model[e.model] += 1

        # Risk levels
        by_risk = defaultdict(int)
        for e in recent_events:
            by_risk[e.risk_level.value] += 1

        return {
            'time_window_minutes': window_minutes,
            'total_requests': total,
            'successful_requests': successful,
            'failed_requests': failed,
            'success_rate': successful / total if total > 0 else 0,
            'total_tokens': total_tokens,
            'avg_tokens_per_request': total_tokens / total if total > 0 else 0,
            'avg_latency_ms': avg_latency,
            'max_latency_ms': max_latency,
            'total_cost_usd': total_cost,
            'avg_cost_per_request': total_cost / total if total > 0 else 0,
            'pii_detections': pii_detected,
            'injection_attempts': injections_detected,
            'by_provider': dict(by_provider),
            'by_model': dict(by_model),
            'by_risk_level': dict(by_risk)
        }

    def clear_old_events(self, days: int = 7):
        """Remove events older than specified days."""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        self.events = [e for e in self.events if e.timestamp >= cutoff_time]
