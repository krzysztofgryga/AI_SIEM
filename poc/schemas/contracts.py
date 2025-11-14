"""
JSON-RPC Contract Schemas for MPC Server.

This module defines the contract between Application Layer and Collection Layer (MPC Server).
All requests/responses follow a strict schema with versioning and validation.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field
from enum import Enum
import uuid


# ============= Enums =============

class SensitivityLevel(str, Enum):
    """Data sensitivity classification."""
    PUBLIC = "public"
    INTERNAL = "internal"
    SENSITIVE = "sensitive"
    PII = "pii"
    CONFIDENTIAL = "confidential"


class RequestType(str, Enum):
    """Type of request."""
    PROCESS_REQUEST = "process_request"
    QUERY = "query"
    HEALTH_CHECK = "health_check"
    BATCH_REQUEST = "batch_request"


class ReturnRoute(str, Enum):
    """How response should be returned."""
    SYNC = "sync"
    ASYNC_WEBHOOK = "async_webhook"
    ASYNC_QUEUE = "async_queue"


class ProcessingHint(str, Enum):
    """Preferred processing backend hint."""
    MODEL_SMALL = "model:small"
    MODEL_LARGE = "model:large"
    MODEL_PRIVATE = "model:private"
    RULE_ENGINE = "rule:engine"
    HYBRID = "hybrid"
    AUTO = "auto"


class ResponseStatus(str, Enum):
    """Response status."""
    OK = "ok"
    ERROR = "error"
    QUEUED = "queued"
    PROCESSING = "processing"


# ============= Source Information =============

class SourceInfo(BaseModel):
    """Information about the source application."""
    application_id: str = Field(..., description="Unique identifier for the application")
    environment: str = Field(default="prod", description="Environment: dev, staging, prod")
    version: Optional[str] = Field(None, description="Application version")
    region: Optional[str] = Field(None, description="Deployment region")


# ============= Authentication =============

class AuthInfo(BaseModel):
    """Authentication information."""
    token: str = Field(..., description="Bearer token or JWT")
    signature: Optional[str] = Field(None, description="Optional HMAC signature for payload integrity")
    client_id: Optional[str] = Field(None, description="Client identifier")


# ============= Processing Configuration =============

class ProcessingConfig(BaseModel):
    """Configuration for processing the request."""
    sensitivity: SensitivityLevel = Field(default=SensitivityLevel.INTERNAL, description="Data sensitivity level")
    processing_hint: ProcessingHint = Field(default=ProcessingHint.AUTO, description="Preferred processing backend")
    return_route: ReturnRoute = Field(default=ReturnRoute.SYNC, description="How to return response")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for async responses")
    timeout_ms: int = Field(default=30000, description="Request timeout in milliseconds")
    enable_pii_detection: bool = Field(default=True, description="Enable PII detection")
    enable_injection_detection: bool = Field(default=True, description="Enable injection detection")
    max_retries: int = Field(default=0, description="Maximum retry attempts")


# ============= Request Schema =============

class MPCRequest(BaseModel):
    """
    Standard MPC Server request.

    This is the contract for all requests from Application Layer to Collection Layer.
    """
    # Protocol metadata
    mpc_version: str = Field(default="1.0", description="MPC protocol version")
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique request identifier")
    idempotency_key: Optional[str] = Field(None, description="Idempotency key for duplicate prevention")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")

    # Source information
    source: SourceInfo = Field(..., description="Source application information")

    # Request type and payload
    type: RequestType = Field(..., description="Type of request")
    payload_schema: str = Field(..., description="Schema version of the payload")
    payload: Dict[str, Any] = Field(..., description="Request payload (schema-validated)")

    # Processing configuration
    config: ProcessingConfig = Field(default_factory=ProcessingConfig, description="Processing configuration")

    # Authentication
    auth: AuthInfo = Field(..., description="Authentication information")

    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "mpc_version": "1.0",
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2025-11-14T12:34:56Z",
                "source": {
                    "application_id": "app-order-service",
                    "environment": "prod",
                    "version": "1.2.3"
                },
                "type": "process_request",
                "payload_schema": "llm.request.v1",
                "payload": {
                    "model": "gpt-4",
                    "prompt": "Analyze this security log",
                    "max_tokens": 1000
                },
                "config": {
                    "sensitivity": "internal",
                    "processing_hint": "model:large",
                    "return_route": "sync"
                },
                "auth": {
                    "token": "mcp-bearer-token-here"
                }
            }
        }


# ============= Response Schema =============

class ProcessingInfo(BaseModel):
    """Information about processing."""
    backend: str = Field(..., description="Backend that processed the request")
    latency_ms: float = Field(..., description="Processing latency in milliseconds")
    cost_usd: Optional[float] = Field(None, description="Cost in USD if applicable")
    confidence: Optional[float] = Field(None, description="Confidence score (0-1)")
    fallback_used: bool = Field(default=False, description="Whether fallback was used")


class ErrorInfo(BaseModel):
    """Error information."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    retry_after_ms: Optional[int] = Field(None, description="Retry after milliseconds")


class MPCResponse(BaseModel):
    """
    Standard MPC Server response.

    This is the contract for all responses from Collection Layer to Application Layer.
    """
    # Protocol metadata
    mpc_version: str = Field(default="1.0", description="MPC protocol version")
    request_id: str = Field(..., description="Original request identifier")
    response_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique response identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    # Status
    status: ResponseStatus = Field(..., description="Response status")

    # Result or error
    result: Optional[Dict[str, Any]] = Field(None, description="Result data if successful")
    error: Optional[ErrorInfo] = Field(None, description="Error information if failed")

    # Processing information
    processing: Optional[ProcessingInfo] = Field(None, description="Processing metadata")

    # Security flags
    security_flags: Dict[str, bool] = Field(default_factory=dict, description="Security detection flags")

    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "mpc_version": "1.0",
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "response_id": "660e8400-e29b-41d4-a716-446655440001",
                "timestamp": "2025-11-14T12:34:57Z",
                "status": "ok",
                "result": {
                    "response": "Analysis complete: No security threats detected.",
                    "tokens": 156
                },
                "processing": {
                    "backend": "openai:gpt-4",
                    "latency_ms": 1234.5,
                    "cost_usd": 0.0023,
                    "confidence": 0.95
                },
                "security_flags": {
                    "has_pii": False,
                    "injection_detected": False
                }
            }
        }


# ============= Event Schema (Async) =============

class EventDelivery(BaseModel):
    """Event delivery metadata."""
    attempts: int = Field(default=0, description="Delivery attempts")
    max_attempts: int = Field(default=5, description="Maximum delivery attempts")
    next_retry_at: Optional[datetime] = Field(None, description="Next retry timestamp")


class MPCEvent(BaseModel):
    """
    Event schema for asynchronous flows.

    Used when MPC Server publishes events to message brokers or webhooks.
    """
    # Event metadata
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique event identifier")
    event_type: str = Field(..., description="Type of event (e.g., 'context.uploaded', 'processing.completed')")
    source: str = Field(..., description="Source service that generated the event")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")

    # Payload
    payload: Dict[str, Any] = Field(..., description="Event payload")

    # Delivery information
    delivery: EventDelivery = Field(default_factory=EventDelivery, description="Delivery metadata")

    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "770e8400-e29b-41d4-a716-446655440002",
                "event_type": "processing.completed",
                "source": "mpc-server",
                "timestamp": "2025-11-14T12:34:58Z",
                "payload": {
                    "request_id": "550e8400-e29b-41d4-a716-446655440000",
                    "status": "completed",
                    "result": {}
                },
                "delivery": {
                    "attempts": 0,
                    "max_attempts": 5
                }
            }
        }


# ============= Payload Schemas =============

class LLMRequestPayload(BaseModel):
    """Standard LLM request payload schema."""
    model: str = Field(..., description="Model identifier")
    prompt: str = Field(..., description="Prompt text")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(None, description="Temperature parameter")
    system_prompt: Optional[str] = Field(None, description="System prompt")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")


class LLMResponsePayload(BaseModel):
    """Standard LLM response payload schema."""
    response: str = Field(..., description="Generated response text")
    tokens: int = Field(..., description="Total tokens used")
    prompt_tokens: Optional[int] = Field(None, description="Prompt tokens")
    completion_tokens: Optional[int] = Field(None, description="Completion tokens")
    finish_reason: Optional[str] = Field(None, description="Finish reason")


# ============= Schema Registry =============

PAYLOAD_SCHEMAS = {
    "llm.request.v1": LLMRequestPayload,
    "llm.response.v1": LLMResponsePayload,
}


def validate_payload(payload_schema: str, payload: Dict[str, Any]) -> Any:
    """
    Validate payload against registered schema.

    Args:
        payload_schema: Schema identifier
        payload: Payload data

    Returns:
        Validated payload object

    Raises:
        ValueError: If schema not found or validation fails
    """
    schema_class = PAYLOAD_SCHEMAS.get(payload_schema)
    if not schema_class:
        raise ValueError(f"Unknown payload schema: {payload_schema}")

    return schema_class(**payload)
