"""
Intelligent Routing System for MPC Server.

Implements multiple routing strategies:
1. Capability Routing - Route by task capability
2. Confidence Cascade - Try cheap first, fallback to expensive
3. Cost-Aware Routing - Consider cost vs SLA
4. Hybrid Pipelines - Combine rules + ML
5. PII-Aware Routing - Route based on sensitivity
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from schemas.contracts import SensitivityLevel, ProcessingHint


logger = logging.getLogger(__name__)


class CapabilityType(str, Enum):
    """Types of processing capabilities."""
    TEXT_GENERATION = "text_generation"
    CLASSIFICATION = "classification"
    EXTRACTION = "extraction"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    CODE_GENERATION = "code_generation"
    ANALYSIS = "analysis"
    SECURITY_SCAN = "security_scan"


class BackendType(str, Enum):
    """Types of backends."""
    LLM_LARGE = "llm_large"  # GPT-4, Claude Opus
    LLM_MEDIUM = "llm_medium"  # GPT-3.5, Claude Sonnet
    LLM_SMALL = "llm_small"  # Claude Haiku, local models
    LLM_PRIVATE = "llm_private"  # On-prem models
    RULE_ENGINE = "rule_engine"  # Deterministic rules
    CLASSIFIER = "classifier"  # Classical ML classifier
    REGEX_ENGINE = "regex_engine"  # Regex-based extraction


@dataclass
class Backend:
    """Backend configuration."""
    id: str
    type: BackendType
    capabilities: List[CapabilityType]
    cost_per_1k_tokens: float
    avg_latency_ms: float
    max_tokens: int
    confidence_threshold: float = 0.0
    pii_allowed: bool = False
    sensitivity_allowed: List[SensitivityLevel] = None

    def __post_init__(self):
        if self.sensitivity_allowed is None:
            self.sensitivity_allowed = [SensitivityLevel.PUBLIC, SensitivityLevel.INTERNAL]


@dataclass
class RoutingDecision:
    """Result of routing decision."""
    backend_id: str
    backend_type: BackendType
    reason: str
    confidence: float
    estimated_cost: float
    estimated_latency_ms: float
    fallback_backends: List[str] = None

    def __post_init__(self):
        if self.fallback_backends is None:
            self.fallback_backends = []


class CapabilityRouter:
    """
    Routes requests based on required capability.

    Maps task types to appropriate backends.
    """

    def __init__(self, backends: List[Backend]):
        """
        Initialize capability router.

        Args:
            backends: List of available backends
        """
        self.backends = {b.id: b for b in backends}
        self.capability_map = self._build_capability_map()

    def _build_capability_map(self) -> Dict[CapabilityType, List[str]]:
        """Build capability to backend mapping."""
        cap_map = {}
        for backend in self.backends.values():
            for capability in backend.capabilities:
                if capability not in cap_map:
                    cap_map[capability] = []
                cap_map[capability].append(backend.id)
        return cap_map

    def get_backends_for_capability(
        self,
        capability: CapabilityType,
        sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL
    ) -> List[str]:
        """
        Get backends that support a capability and sensitivity level.

        Args:
            capability: Required capability
            sensitivity: Data sensitivity level

        Returns:
            List of backend IDs
        """
        candidate_backends = self.capability_map.get(capability, [])

        # Filter by sensitivity
        allowed = []
        for backend_id in candidate_backends:
            backend = self.backends[backend_id]
            if sensitivity in backend.sensitivity_allowed:
                allowed.append(backend_id)

        return allowed


class ConfidenceCascadeRouter:
    """
    Implements confidence cascade / fallback routing.

    Strategy:
    1. Try cheapest/fastest option first
    2. If confidence < threshold, try next option
    3. Continue until confidence met or options exhausted
    """

    def __init__(self, backends: List[Backend]):
        """
        Initialize cascade router.

        Args:
            backends: List of available backends
        """
        self.backends = {b.id: b for b in backends}

    def get_cascade_order(
        self,
        candidate_backends: List[str],
        optimize_for: str = "cost"  # "cost" or "latency"
    ) -> List[str]:
        """
        Get backends in cascade order (cheap/fast to expensive/slow).

        Args:
            candidate_backends: List of candidate backend IDs
            optimize_for: Optimization criterion

        Returns:
            Ordered list of backend IDs
        """
        backends = [self.backends[bid] for bid in candidate_backends]

        if optimize_for == "cost":
            # Sort by cost ascending
            sorted_backends = sorted(backends, key=lambda b: b.cost_per_1k_tokens)
        else:  # latency
            # Sort by latency ascending
            sorted_backends = sorted(backends, key=lambda b: b.avg_latency_ms)

        return [b.id for b in sorted_backends]

    def get_fallback_chain(
        self,
        primary_backend: str,
        candidate_backends: List[str],
        max_fallbacks: int = 2
    ) -> List[str]:
        """
        Get fallback chain for a primary backend.

        Args:
            primary_backend: Primary backend ID
            candidate_backends: Other candidate backends
            max_fallbacks: Maximum fallback options

        Returns:
            List of fallback backend IDs
        """
        # Remove primary from candidates
        candidates = [b for b in candidate_backends if b != primary_backend]

        # Get cascade order
        ordered = self.get_cascade_order(candidates, optimize_for="cost")

        # Return top N fallbacks (starting from where primary would be)
        primary_cost = self.backends[primary_backend].cost_per_1k_tokens

        # Get backends more expensive than primary
        fallbacks = []
        for backend_id in ordered:
            if self.backends[backend_id].cost_per_1k_tokens > primary_cost:
                fallbacks.append(backend_id)
                if len(fallbacks) >= max_fallbacks:
                    break

        return fallbacks


class CostAwareRouter:
    """
    Routes based on cost vs SLA requirements.

    Considers:
    - Budget constraints
    - Latency SLA
    - Quality requirements (confidence threshold)
    """

    def __init__(self, backends: List[Backend]):
        """
        Initialize cost-aware router.

        Args:
            backends: List of available backends
        """
        self.backends = {b.id: b for b in backends}

    def select_backend(
        self,
        candidate_backends: List[str],
        max_cost: float = 1.0,
        max_latency_ms: float = 5000,
        min_confidence: float = 0.8,
        estimated_tokens: int = 1000
    ) -> Optional[str]:
        """
        Select best backend given constraints.

        Args:
            candidate_backends: Candidate backend IDs
            max_cost: Maximum cost in USD
            max_latency_ms: Maximum latency in ms
            min_confidence: Minimum confidence threshold
            estimated_tokens: Estimated tokens for cost calculation

        Returns:
            Selected backend ID or None
        """
        valid_backends = []

        for backend_id in candidate_backends:
            backend = self.backends[backend_id]

            # Check cost constraint
            estimated_cost = (estimated_tokens / 1000) * backend.cost_per_1k_tokens
            if estimated_cost > max_cost:
                continue

            # Check latency constraint
            if backend.avg_latency_ms > max_latency_ms:
                continue

            # Check confidence constraint
            if backend.confidence_threshold < min_confidence:
                continue

            valid_backends.append((backend_id, estimated_cost, backend.avg_latency_ms))

        if not valid_backends:
            return None

        # Select backend with best cost/quality ratio
        # Prefer lower cost, but ensure quality
        valid_backends.sort(key=lambda x: (x[1], x[2]))  # Sort by cost, then latency

        return valid_backends[0][0]


class IntelligentRouter:
    """
    Main intelligent routing system combining all strategies.
    """

    def __init__(self, backends: List[Backend]):
        """
        Initialize intelligent router.

        Args:
            backends: List of available backends
        """
        self.backends = {b.id: b for b in backends}
        self.capability_router = CapabilityRouter(backends)
        self.cascade_router = ConfidenceCascadeRouter(backends)
        self.cost_router = CostAwareRouter(backends)

    def route(
        self,
        capability: CapabilityType,
        sensitivity: SensitivityLevel,
        processing_hint: ProcessingHint = ProcessingHint.AUTO,
        max_cost: float = 1.0,
        max_latency_ms: float = 5000,
        estimated_tokens: int = 1000,
        use_cascade: bool = True
    ) -> RoutingDecision:
        """
        Make routing decision.

        Args:
            capability: Required capability
            sensitivity: Data sensitivity
            processing_hint: Processing hint from client
            max_cost: Maximum cost constraint
            max_latency_ms: Maximum latency constraint
            estimated_tokens: Estimated tokens
            use_cascade: Whether to use cascade/fallback

        Returns:
            RoutingDecision
        """
        # Step 1: Get backends by capability and sensitivity
        candidates = self.capability_router.get_backends_for_capability(
            capability,
            sensitivity
        )

        if not candidates:
            raise ValueError(
                f"No backends available for capability '{capability}' "
                f"with sensitivity '{sensitivity}'"
            )

        logger.info(f"Candidate backends for {capability}/{sensitivity}: {candidates}")

        # Step 2: Apply processing hint if specified
        if processing_hint != ProcessingHint.AUTO:
            candidates = self._filter_by_hint(candidates, processing_hint)

        if not candidates:
            raise ValueError(f"No backends match processing hint '{processing_hint}'")

        # Step 3: Select primary backend using cost-aware routing
        primary_backend_id = self.cost_router.select_backend(
            candidates,
            max_cost=max_cost,
            max_latency_ms=max_latency_ms,
            estimated_tokens=estimated_tokens
        )

        if not primary_backend_id:
            # Relax constraints and try again with just sensitivity
            logger.warning("No backend meets all constraints, selecting cheapest available")
            cascade_order = self.cascade_router.get_cascade_order(candidates, optimize_for="cost")
            primary_backend_id = cascade_order[0] if cascade_order else candidates[0]

        primary_backend = self.backends[primary_backend_id]

        # Step 4: Get fallback chain if cascade enabled
        fallback_backends = []
        if use_cascade:
            fallback_backends = self.cascade_router.get_fallback_chain(
                primary_backend_id,
                candidates,
                max_fallbacks=2
            )

        # Step 5: Calculate estimates
        estimated_cost = (estimated_tokens / 1000) * primary_backend.cost_per_1k_tokens
        estimated_latency = primary_backend.avg_latency_ms

        return RoutingDecision(
            backend_id=primary_backend_id,
            backend_type=primary_backend.type,
            reason=f"Selected based on capability={capability}, sensitivity={sensitivity}, hint={processing_hint}",
            confidence=primary_backend.confidence_threshold,
            estimated_cost=estimated_cost,
            estimated_latency_ms=estimated_latency,
            fallback_backends=fallback_backends
        )

    def _filter_by_hint(
        self,
        candidates: List[str],
        hint: ProcessingHint
    ) -> List[str]:
        """Filter backends by processing hint."""
        hint_to_type = {
            ProcessingHint.MODEL_SMALL: [BackendType.LLM_SMALL],
            ProcessingHint.MODEL_LARGE: [BackendType.LLM_LARGE],
            ProcessingHint.MODEL_PRIVATE: [BackendType.LLM_PRIVATE],
            ProcessingHint.RULE_ENGINE: [BackendType.RULE_ENGINE, BackendType.REGEX_ENGINE],
            ProcessingHint.HYBRID: None,  # Allow all
            ProcessingHint.AUTO: None,  # Allow all
        }

        allowed_types = hint_to_type.get(hint)
        if allowed_types is None:
            return candidates

        return [
            bid for bid in candidates
            if self.backends[bid].type in allowed_types
        ]


# ============= Default Backend Registry =============

def get_default_backends() -> List[Backend]:
    """Get default backend configuration."""
    return [
        # LLM Backends
        Backend(
            id="openai:gpt-4",
            type=BackendType.LLM_LARGE,
            capabilities=[
                CapabilityType.TEXT_GENERATION,
                CapabilityType.CLASSIFICATION,
                CapabilityType.EXTRACTION,
                CapabilityType.SUMMARIZATION,
                CapabilityType.ANALYSIS,
                CapabilityType.CODE_GENERATION,
            ],
            cost_per_1k_tokens=0.03,
            avg_latency_ms=2000,
            max_tokens=8192,
            confidence_threshold=0.9,
            pii_allowed=False,
            sensitivity_allowed=[SensitivityLevel.PUBLIC, SensitivityLevel.INTERNAL]
        ),
        Backend(
            id="openai:gpt-3.5-turbo",
            type=BackendType.LLM_MEDIUM,
            capabilities=[
                CapabilityType.TEXT_GENERATION,
                CapabilityType.CLASSIFICATION,
                CapabilityType.EXTRACTION,
                CapabilityType.SUMMARIZATION,
            ],
            cost_per_1k_tokens=0.0015,
            avg_latency_ms=800,
            max_tokens=4096,
            confidence_threshold=0.8,
            pii_allowed=False,
            sensitivity_allowed=[SensitivityLevel.PUBLIC, SensitivityLevel.INTERNAL]
        ),
        Backend(
            id="anthropic:claude-3-opus",
            type=BackendType.LLM_LARGE,
            capabilities=[
                CapabilityType.TEXT_GENERATION,
                CapabilityType.CLASSIFICATION,
                CapabilityType.EXTRACTION,
                CapabilityType.SUMMARIZATION,
                CapabilityType.ANALYSIS,
                CapabilityType.CODE_GENERATION,
            ],
            cost_per_1k_tokens=0.015,
            avg_latency_ms=1800,
            max_tokens=4096,
            confidence_threshold=0.95,
            pii_allowed=False,
            sensitivity_allowed=[SensitivityLevel.PUBLIC, SensitivityLevel.INTERNAL]
        ),
        Backend(
            id="ollama:llama2",
            type=BackendType.LLM_PRIVATE,
            capabilities=[
                CapabilityType.TEXT_GENERATION,
                CapabilityType.CLASSIFICATION,
                CapabilityType.SUMMARIZATION,
            ],
            cost_per_1k_tokens=0.0,  # Free (local)
            avg_latency_ms=3000,
            max_tokens=2048,
            confidence_threshold=0.7,
            pii_allowed=True,
            sensitivity_allowed=[
                SensitivityLevel.PUBLIC,
                SensitivityLevel.INTERNAL,
                SensitivityLevel.SENSITIVE,
                SensitivityLevel.PII,
            ]
        ),
        # Rule-based backends
        Backend(
            id="rules:pii-detector",
            type=BackendType.REGEX_ENGINE,
            capabilities=[
                CapabilityType.EXTRACTION,
                CapabilityType.SECURITY_SCAN,
            ],
            cost_per_1k_tokens=0.0,
            avg_latency_ms=50,
            max_tokens=100000,
            confidence_threshold=0.85,
            pii_allowed=True,
            sensitivity_allowed=[
                SensitivityLevel.PUBLIC,
                SensitivityLevel.INTERNAL,
                SensitivityLevel.SENSITIVE,
                SensitivityLevel.PII,
            ]
        ),
        Backend(
            id="rules:injection-detector",
            type=BackendType.RULE_ENGINE,
            capabilities=[
                CapabilityType.SECURITY_SCAN,
            ],
            cost_per_1k_tokens=0.0,
            avg_latency_ms=30,
            max_tokens=100000,
            confidence_threshold=0.9,
            pii_allowed=True,
            sensitivity_allowed=[
                SensitivityLevel.PUBLIC,
                SensitivityLevel.INTERNAL,
                SensitivityLevel.SENSITIVE,
                SensitivityLevel.PII,
            ]
        ),
    ]
