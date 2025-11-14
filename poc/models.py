"""
Data models for AI monitoring POC.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum


class EventType(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    ANOMALY = "anomaly"


class Provider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    CUSTOM = "custom"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TokenUsage(BaseModel):
    """Token usage information."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class AIRequest(BaseModel):
    """Normalized AI request."""
    id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    provider: Provider
    model: str
    prompt: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AIResponse(BaseModel):
    """Normalized AI response."""
    request_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    content: str
    finish_reason: Optional[str] = None
    tokens: TokenUsage
    latency_ms: float
    cost_usd: float = 0.0
    model_version: Optional[str] = None


class AIEvent(BaseModel):
    """Complete AI interaction event."""
    id: str
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    provider: Provider
    model: str

    # Request data
    prompt: Optional[str] = None
    prompt_length: int = 0

    # Response data
    response: Optional[str] = None
    response_length: int = 0

    # Metrics
    latency_ms: Optional[float] = None
    tokens: Optional[TokenUsage] = None
    cost_usd: float = 0.0

    # Status
    success: bool = True
    error_message: Optional[str] = None

    # Security
    has_pii: bool = False
    injection_detected: bool = False
    risk_level: RiskLevel = RiskLevel.LOW

    # Metadata
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Anomaly(BaseModel):
    """Detected anomaly."""
    id: str
    event_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    anomaly_type: str
    severity: RiskLevel
    description: str
    details: Dict[str, Any] = Field(default_factory=dict)
    recommended_action: Optional[str] = None


class AggregatedMetrics(BaseModel):
    """Aggregated metrics for a time window."""
    window_start: datetime
    window_end: datetime
    provider: Optional[str] = None
    model: Optional[str] = None

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0

    total_tokens: int = 0
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0

    total_cost_usd: float = 0.0

    anomalies_detected: int = 0
    security_incidents: int = 0
