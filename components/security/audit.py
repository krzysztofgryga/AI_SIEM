"""
Audit logging for security and compliance.

Implements structured audit logs with PII protection.
"""
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum
import logging


class AuditEventType(str, Enum):
    """Types of audit events."""
    REQUEST_RECEIVED = "request.received"
    REQUEST_AUTHORIZED = "request.authorized"
    REQUEST_DENIED = "request.denied"
    PROCESSING_STARTED = "processing.started"
    PROCESSING_COMPLETED = "processing.completed"
    PROCESSING_FAILED = "processing.failed"
    PII_DETECTED = "pii.detected"
    INJECTION_DETECTED = "injection.detected"
    ANOMALY_DETECTED = "anomaly.detected"
    SECURITY_VIOLATION = "security.violation"
    DATA_ACCESS = "data.access"


class Outcome(str, Enum):
    """Audit event outcomes."""
    SUCCESS = "success"
    FAILURE = "failure"
    DENIED = "denied"
    ERROR = "error"


@dataclass
class AuditEvent:
    """
    Structured audit event.

    Follows security best practices:
    - No PII in logs (use hashes)
    - Timestamp
    - Actor (who)
    - Action (what)
    - Resource (on what)
    - Outcome (result)
    - Context (additional info)
    """
    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    actor: str  # client_id or user_id (hashed if PII)
    action: str
    resource: str
    outcome: Outcome
    sensitivity_level: Optional[str] = None
    context: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['event_type'] = self.event_type.value
        data['outcome'] = self.outcome.value
        return data

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


class AuditLogger:
    """
    Audit logger with PII protection and structured logging.
    """

    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        enable_console: bool = False,
        enable_file: bool = True,
        log_file: str = "audit.log"
    ):
        """
        Initialize audit logger.

        Args:
            logger: Optional custom logger
            enable_console: Enable console output
            enable_file: Enable file output
            log_file: Audit log file path
        """
        if logger:
            self.logger = logger
        else:
            self.logger = self._setup_logger(enable_console, enable_file, log_file)

    def _setup_logger(
        self,
        enable_console: bool,
        enable_file: bool,
        log_file: str
    ) -> logging.Logger:
        """Setup structured audit logger."""
        logger = logging.getLogger("audit")
        logger.setLevel(logging.INFO)
        logger.propagate = False

        # Clear existing handlers
        logger.handlers = []

        formatter = logging.Formatter(
            '%(message)s'  # We'll use JSON format
        )

        if enable_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        if enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger

    def log(self, event: AuditEvent):
        """
        Log audit event.

        Args:
            event: Audit event to log
        """
        self.logger.info(event.to_json())

    def log_request(
        self,
        request_id: str,
        client_id: str,
        action: str,
        sensitivity: str,
        outcome: Outcome,
        context: Optional[Dict[str, Any]] = None
    ):
        """Log a request event."""
        event = AuditEvent(
            event_id=request_id,
            timestamp=datetime.utcnow(),
            event_type=AuditEventType.REQUEST_RECEIVED,
            actor=self._hash_if_pii(client_id),
            action=action,
            resource=f"request:{request_id}",
            outcome=outcome,
            sensitivity_level=sensitivity,
            context=context or {}
        )
        self.log(event)

    def log_authorization(
        self,
        request_id: str,
        client_id: str,
        action: str,
        is_authorized: bool,
        reason: Optional[str] = None
    ):
        """Log an authorization decision."""
        event = AuditEvent(
            event_id=request_id,
            timestamp=datetime.utcnow(),
            event_type=AuditEventType.REQUEST_AUTHORIZED if is_authorized else AuditEventType.REQUEST_DENIED,
            actor=self._hash_if_pii(client_id),
            action=action,
            resource=f"request:{request_id}",
            outcome=Outcome.SUCCESS if is_authorized else Outcome.DENIED,
            context={'reason': reason} if reason else {}
        )
        self.log(event)

    def log_pii_detection(
        self,
        request_id: str,
        pii_types: List[str],
        action_taken: str
    ):
        """Log PII detection."""
        event = AuditEvent(
            event_id=request_id,
            timestamp=datetime.utcnow(),
            event_type=AuditEventType.PII_DETECTED,
            actor="system",
            action="pii_detection",
            resource=f"request:{request_id}",
            outcome=Outcome.SUCCESS,
            sensitivity_level="sensitive",
            context={
                'pii_types': pii_types,
                'action_taken': action_taken
            }
        )
        self.log(event)

    def log_security_violation(
        self,
        request_id: str,
        violation_type: str,
        details: Dict[str, Any]
    ):
        """Log security violation."""
        event = AuditEvent(
            event_id=request_id,
            timestamp=datetime.utcnow(),
            event_type=AuditEventType.SECURITY_VIOLATION,
            actor="system",
            action="security_check",
            resource=f"request:{request_id}",
            outcome=Outcome.DENIED,
            sensitivity_level="critical",
            context={
                'violation_type': violation_type,
                'details': details
            }
        )
        self.log(event)

    def log_processing(
        self,
        request_id: str,
        backend: str,
        outcome: Outcome,
        latency_ms: Optional[float] = None,
        cost_usd: Optional[float] = None,
        error: Optional[str] = None
    ):
        """Log processing event."""
        event = AuditEvent(
            event_id=request_id,
            timestamp=datetime.utcnow(),
            event_type=AuditEventType.PROCESSING_COMPLETED if outcome == Outcome.SUCCESS else AuditEventType.PROCESSING_FAILED,
            actor="system",
            action="process",
            resource=f"backend:{backend}",
            outcome=outcome,
            context={
                'latency_ms': latency_ms,
                'cost_usd': cost_usd,
                'error': error
            }
        )
        self.log(event)

    @staticmethod
    def _hash_if_pii(value: str) -> str:
        """
        Hash value if it looks like PII.

        For audit logs, we hash user identifiers to protect privacy
        while maintaining traceability.
        """
        # Simple heuristic: if contains @, phone pattern, etc., hash it
        if '@' in value or any(c.isdigit() for c in value):
            return hashlib.sha256(value.encode()).hexdigest()[:16]
        return value


class AuditQuery:
    """
    Query audit logs for compliance and investigation.
    """

    def __init__(self, log_file: str = "audit.log"):
        """
        Initialize audit query.

        Args:
            log_file: Path to audit log file
        """
        self.log_file = log_file

    def query(
        self,
        event_type: Optional[AuditEventType] = None,
        actor: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        outcome: Optional[Outcome] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query audit logs.

        Args:
            event_type: Filter by event type
            actor: Filter by actor
            start_time: Filter by start time
            end_time: Filter by end time
            outcome: Filter by outcome
            limit: Maximum results

        Returns:
            List of matching audit events
        """
        results = []

        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())

                        # Apply filters
                        if event_type and event.get('event_type') != event_type.value:
                            continue

                        if actor and event.get('actor') != actor:
                            continue

                        if outcome and event.get('outcome') != outcome.value:
                            continue

                        event_time = datetime.fromisoformat(event.get('timestamp'))

                        if start_time and event_time < start_time:
                            continue

                        if end_time and event_time > end_time:
                            continue

                        results.append(event)

                        if len(results) >= limit:
                            break

                    except json.JSONDecodeError:
                        continue

        except FileNotFoundError:
            pass

        return results

    def get_security_violations(
        self,
        hours: int = 24,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent security violations."""
        start_time = datetime.utcnow() - timedelta(hours=hours)
        return self.query(
            event_type=AuditEventType.SECURITY_VIOLATION,
            start_time=start_time,
            limit=limit
        )

    def get_pii_detections(
        self,
        hours: int = 24,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent PII detections."""
        start_time = datetime.utcnow() - timedelta(hours=hours)
        return self.query(
            event_type=AuditEventType.PII_DETECTED,
            start_time=start_time,
            limit=limit
        )
