"""
AI Agent Monitoring POC

A minimal proof-of-concept for monitoring AI agents with:
- Data collection (OpenAI, Anthropic)
- Data processing (normalization, enrichment)
- Anomaly detection (security, cost, performance)
"""

from .models import (
    AIEvent,
    AIRequest,
    AIResponse,
    Anomaly,
    TokenUsage,
    EventType,
    Provider,
    RiskLevel
)

from .collector import (
    OpenAICollector,
    AnthropicCollector
)

from .processor import (
    EventProcessor,
    EventAggregator
)

from .analyzer import (
    AnomalyDetector
)

from .storage import (
    EventStorage
)

__version__ = "0.1.0"
__all__ = [
    # Models
    "AIEvent",
    "AIRequest",
    "AIResponse",
    "Anomaly",
    "TokenUsage",
    "EventType",
    "Provider",
    "RiskLevel",
    # Collectors
    "OpenAICollector",
    "AnthropicCollector",
    # Processing
    "EventProcessor",
    "EventAggregator",
    # Analysis
    "AnomalyDetector",
    # Storage
    "EventStorage",
]
