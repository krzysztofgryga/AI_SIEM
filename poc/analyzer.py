"""
Anomaly detection and analysis.
"""
import uuid
from typing import List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

from models import AIEvent, Anomaly, RiskLevel


class AnomalyDetector:
    """Detect anomalies in AI agent behavior."""

    def __init__(self, config: dict = None):
        self.config = config or {
            'cost_threshold_usd': 0.5,
            'latency_threshold_ms': 5000,
            'error_rate_threshold': 0.1,
            'token_threshold': 8000,
            'spike_multiplier': 3.0
        }
        self.baseline_metrics = {}

    def analyze_event(self, event: AIEvent, recent_events: List[AIEvent]) -> List[Anomaly]:
        """Analyze a single event for anomalies."""
        anomalies = []

        # Check for high cost
        if event.cost_usd > self.config['cost_threshold_usd']:
            anomalies.append(Anomaly(
                id=str(uuid.uuid4()),
                event_id=event.id,
                anomaly_type='high_cost',
                severity=RiskLevel.HIGH,
                description=f'Request cost ${event.cost_usd:.4f} exceeds threshold ${self.config["cost_threshold_usd"]}',
                details={'cost': event.cost_usd, 'threshold': self.config['cost_threshold_usd']},
                recommended_action='Review model usage and consider using a cheaper model'
            ))

        # Check for high latency
        if event.latency_ms and event.latency_ms > self.config['latency_threshold_ms']:
            anomalies.append(Anomaly(
                id=str(uuid.uuid4()),
                event_id=event.id,
                anomaly_type='high_latency',
                severity=RiskLevel.MEDIUM,
                description=f'Request latency {event.latency_ms:.0f}ms exceeds threshold {self.config["latency_threshold_ms"]}ms',
                details={'latency_ms': event.latency_ms, 'threshold': self.config['latency_threshold_ms']},
                recommended_action='Check API service status and network conditions'
            ))

        # Check for excessive tokens
        if event.tokens and event.tokens.total_tokens > self.config['token_threshold']:
            anomalies.append(Anomaly(
                id=str(uuid.uuid4()),
                event_id=event.id,
                anomaly_type='high_token_usage',
                severity=RiskLevel.MEDIUM,
                description=f'Token usage {event.tokens.total_tokens} exceeds threshold {self.config["token_threshold"]}',
                details={'tokens': event.tokens.total_tokens, 'threshold': self.config['token_threshold']},
                recommended_action='Review prompt size and implement token limits'
            ))

        # Check for errors
        if not event.success:
            anomalies.append(Anomaly(
                id=str(uuid.uuid4()),
                event_id=event.id,
                anomaly_type='request_failure',
                severity=RiskLevel.HIGH,
                description=f'Request failed: {event.error_message}',
                details={'error': event.error_message},
                recommended_action='Check error logs and API credentials'
            ))

        # Check for security issues
        if event.injection_detected:
            anomalies.append(Anomaly(
                id=str(uuid.uuid4()),
                event_id=event.id,
                anomaly_type='prompt_injection',
                severity=RiskLevel.CRITICAL,
                description='Potential prompt injection attack detected',
                details={'prompt_preview': event.prompt[:200] if event.prompt else ''},
                recommended_action='BLOCK REQUEST - Implement input validation and filtering'
            ))

        # Check for PII
        if event.has_pii:
            anomalies.append(Anomaly(
                id=str(uuid.uuid4()),
                event_id=event.id,
                anomaly_type='pii_detected',
                severity=RiskLevel.HIGH,
                description='Personally Identifiable Information (PII) detected',
                details={},
                recommended_action='Implement PII scrubbing and review data handling policies'
            ))

        # Check for cost spikes (compared to recent average)
        if recent_events and len(recent_events) > 10:
            recent_costs = [e.cost_usd for e in recent_events[-20:] if e.cost_usd > 0]
            if recent_costs:
                avg_cost = statistics.mean(recent_costs)
                if event.cost_usd > avg_cost * self.config['spike_multiplier']:
                    anomalies.append(Anomaly(
                        id=str(uuid.uuid4()),
                        event_id=event.id,
                        anomaly_type='cost_spike',
                        severity=RiskLevel.HIGH,
                        description=f'Cost spike detected: {event.cost_usd:.4f} vs avg {avg_cost:.4f}',
                        details={
                            'current_cost': event.cost_usd,
                            'average_cost': avg_cost,
                            'multiplier': event.cost_usd / avg_cost if avg_cost > 0 else 0
                        },
                        recommended_action='Investigate unusual activity'
                    ))

        # Check for latency spikes
        if recent_events and len(recent_events) > 10 and event.latency_ms:
            recent_latencies = [e.latency_ms for e in recent_events[-20:] if e.latency_ms]
            if recent_latencies:
                avg_latency = statistics.mean(recent_latencies)
                if event.latency_ms > avg_latency * self.config['spike_multiplier']:
                    anomalies.append(Anomaly(
                        id=str(uuid.uuid4()),
                        event_id=event.id,
                        anomaly_type='latency_spike',
                        severity=RiskLevel.MEDIUM,
                        description=f'Latency spike: {event.latency_ms:.0f}ms vs avg {avg_latency:.0f}ms',
                        details={
                            'current_latency': event.latency_ms,
                            'average_latency': avg_latency
                        },
                        recommended_action='Monitor API performance'
                    ))

        return anomalies

    def analyze_patterns(self, events: List[AIEvent], window_minutes: int = 60) -> List[Anomaly]:
        """Analyze patterns across multiple events."""
        anomalies = []
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent = [e for e in events if e.timestamp >= cutoff_time]

        if len(recent) < 10:  # Need enough data
            return anomalies

        # Calculate error rate
        total = len(recent)
        errors = sum(1 for e in recent if not e.success)
        error_rate = errors / total if total > 0 else 0

        if error_rate > self.config['error_rate_threshold']:
            anomalies.append(Anomaly(
                id=str(uuid.uuid4()),
                event_id='pattern',
                anomaly_type='high_error_rate',
                severity=RiskLevel.CRITICAL,
                description=f'High error rate: {error_rate:.1%} in last {window_minutes} minutes',
                details={
                    'error_rate': error_rate,
                    'total_requests': total,
                    'failed_requests': errors,
                    'threshold': self.config['error_rate_threshold']
                },
                recommended_action='Check API status and investigate root cause'
            ))

        # Check for repeated failures on same model
        model_errors = defaultdict(int)
        model_totals = defaultdict(int)
        for e in recent:
            model_totals[e.model] += 1
            if not e.success:
                model_errors[e.model] += 1

        for model, error_count in model_errors.items():
            total_count = model_totals[model]
            model_error_rate = error_count / total_count if total_count > 0 else 0
            if model_error_rate > self.config['error_rate_threshold'] and total_count >= 5:
                anomalies.append(Anomaly(
                    id=str(uuid.uuid4()),
                    event_id='pattern',
                    anomaly_type='model_errors',
                    severity=RiskLevel.HIGH,
                    description=f'High error rate for model {model}: {model_error_rate:.1%}',
                    details={
                        'model': model,
                        'error_rate': model_error_rate,
                        'errors': error_count,
                        'total': total_count
                    },
                    recommended_action=f'Check {model} availability or switch to backup model'
                ))

        # Check for unusual activity patterns (rapid requests)
        if len(recent) > 100:  # More than 100 requests in window
            requests_per_minute = len(recent) / window_minutes
            if requests_per_minute > 50:  # More than 50 req/min
                anomalies.append(Anomaly(
                    id=str(uuid.uuid4()),
                    event_id='pattern',
                    anomaly_type='high_request_rate',
                    severity=RiskLevel.MEDIUM,
                    description=f'Unusual request rate: {requests_per_minute:.1f} req/min',
                    details={
                        'requests_per_minute': requests_per_minute,
                        'total_requests': len(recent)
                    },
                    recommended_action='Check for runaway processes or DDoS'
                ))

        # Check for cost accumulation
        total_cost = sum(e.cost_usd for e in recent)
        hourly_cost = total_cost / (window_minutes / 60)
        if hourly_cost > 10.0:  # More than $10/hour
            anomalies.append(Anomaly(
                id=str(uuid.uuid4()),
                event_id='pattern',
                anomaly_type='high_cost_rate',
                severity=RiskLevel.HIGH,
                description=f'High cost rate: ${hourly_cost:.2f}/hour',
                details={
                    'hourly_cost': hourly_cost,
                    'total_cost': total_cost,
                    'window_minutes': window_minutes
                },
                recommended_action='Review usage and implement cost controls'
            ))

        return anomalies
