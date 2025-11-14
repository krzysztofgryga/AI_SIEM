"""
Processing Backends - Actual implementation of processing logic.

Each backend implements a specific processing capability:
- LLM backends (OpenAI, Anthropic, Ollama, etc.)
- Rule-based backends (regex, classifiers)
- Hybrid backends (combine multiple approaches)
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
import logging

from models import AIEvent, EventType, Provider, TokenUsage, RiskLevel


logger = logging.getLogger(__name__)


class ProcessingBackend(ABC):
    """Base class for all processing backends."""

    def __init__(self, backend_id: str):
        """
        Initialize backend.

        Args:
            backend_id: Unique backend identifier
        """
        self.backend_id = backend_id

    @abstractmethod
    async def process(
        self,
        prompt: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a request.

        Args:
            prompt: Input prompt
            params: Optional parameters

        Returns:
            Processing result with response, tokens, cost, etc.
        """
        pass

    def _create_event(
        self,
        prompt: str,
        response: str,
        latency_ms: float,
        tokens: TokenUsage,
        cost_usd: float,
        provider: Provider,
        model: str,
        success: bool = True,
        error: Optional[str] = None
    ) -> AIEvent:
        """Create AIEvent for monitoring."""
        import uuid

        return AIEvent(
            id=str(uuid.uuid4()),
            event_type=EventType.RESPONSE if success else EventType.ERROR,
            provider=provider,
            model=model,
            prompt=prompt,
            prompt_length=len(prompt),
            response=response,
            response_length=len(response) if response else 0,
            latency_ms=latency_ms,
            tokens=tokens,
            cost_usd=cost_usd,
            success=success,
            error_message=error
        )


class OpenAIBackend(ProcessingBackend):
    """OpenAI processing backend."""

    def __init__(
        self,
        backend_id: str = "openai:gpt-3.5-turbo",
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo"
    ):
        """
        Initialize OpenAI backend.

        Args:
            backend_id: Backend identifier
            api_key: OpenAI API key
            model: Model to use
        """
        super().__init__(backend_id)
        self.model = model
        self.api_key = api_key

    async def process(
        self,
        prompt: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process using OpenAI API."""
        start_time = time.time()

        try:
            # Import here to avoid dependency if not using OpenAI
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)

            # Call OpenAI
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                **params or {}
            )

            latency_ms = (time.time() - start_time) * 1000

            # Extract response
            content = response.choices[0].message.content
            tokens = TokenUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens
            )

            # Calculate cost (simplified)
            cost_usd = (tokens.total_tokens / 1000) * 0.002

            return {
                'response': content,
                'tokens': tokens.total_tokens,
                'prompt_tokens': tokens.prompt_tokens,
                'completion_tokens': tokens.completion_tokens,
                'cost': cost_usd,
                'latency_ms': latency_ms,
                'backend': self.backend_id,
                'confidence': 0.9
            }

        except Exception as e:
            logger.error(f"OpenAI backend error: {str(e)}")
            raise


class OllamaBackend(ProcessingBackend):
    """Ollama (local LLM) processing backend."""

    def __init__(
        self,
        backend_id: str = "ollama:llama2",
        base_url: str = "http://localhost:11434",
        model: str = "llama2"
    ):
        """
        Initialize Ollama backend.

        Args:
            backend_id: Backend identifier
            base_url: Ollama server URL
            model: Model to use
        """
        super().__init__(backend_id)
        self.base_url = base_url
        self.model = model

    async def process(
        self,
        prompt: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process using Ollama."""
        start_time = time.time()

        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        **(params or {})
                    },
                    timeout=30.0
                )

                response.raise_for_status()
                result = response.json()

            latency_ms = (time.time() - start_time) * 1000

            return {
                'response': result.get('response', ''),
                'tokens': result.get('eval_count', 0) + result.get('prompt_eval_count', 0),
                'prompt_tokens': result.get('prompt_eval_count', 0),
                'completion_tokens': result.get('eval_count', 0),
                'cost': 0.0,  # Free (local)
                'latency_ms': latency_ms,
                'backend': self.backend_id,
                'confidence': 0.75
            }

        except Exception as e:
            logger.error(f"Ollama backend error: {str(e)}")
            raise


class RuleBasedBackend(ProcessingBackend):
    """Rule-based processing backend (deterministic)."""

    def __init__(self, backend_id: str = "rules:classifier"):
        """Initialize rule-based backend."""
        super().__init__(backend_id)

    async def process(
        self,
        prompt: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process using rules."""
        start_time = time.time()

        # Simple rule-based processing
        # In production, this would be more sophisticated

        response = self._apply_rules(prompt)
        latency_ms = (time.time() - start_time) * 1000

        return {
            'response': response,
            'tokens': len(response.split()),
            'prompt_tokens': len(prompt.split()),
            'completion_tokens': len(response.split()),
            'cost': 0.0,
            'latency_ms': latency_ms,
            'backend': self.backend_id,
            'confidence': 1.0  # Deterministic
        }

    def _apply_rules(self, prompt: str) -> str:
        """Apply rule-based logic."""
        prompt_lower = prompt.lower()

        # Example rules
        if 'hello' in prompt_lower or 'hi' in prompt_lower:
            return "Greeting detected. Classification: GREETING"

        if any(word in prompt_lower for word in ['threat', 'attack', 'malicious']):
            return "Security concern detected. Classification: SECURITY_ALERT"

        if any(word in prompt_lower for word in ['error', 'exception', 'failed']):
            return "Error detected. Classification: ERROR_LOG"

        return "General query. Classification: UNKNOWN"


class HybridBackend(ProcessingBackend):
    """
    Hybrid backend - combines rules + ML.

    Strategy:
    1. Try rules first (fast, cheap, deterministic)
    2. If confidence < threshold, fallback to LLM
    """

    def __init__(
        self,
        backend_id: str = "hybrid:rule-llm",
        rule_backend: Optional[ProcessingBackend] = None,
        llm_backend: Optional[ProcessingBackend] = None,
        confidence_threshold: float = 0.8
    ):
        """
        Initialize hybrid backend.

        Args:
            backend_id: Backend identifier
            rule_backend: Rule-based backend
            llm_backend: LLM backend
            confidence_threshold: Threshold for fallback
        """
        super().__init__(backend_id)
        self.rule_backend = rule_backend or RuleBasedBackend()
        self.llm_backend = llm_backend
        self.confidence_threshold = confidence_threshold

    async def process(
        self,
        prompt: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process using hybrid approach."""

        # Step 1: Try rules first
        rule_result = await self.rule_backend.process(prompt, params)

        # Check confidence
        if rule_result['confidence'] >= self.confidence_threshold:
            rule_result['strategy'] = 'rule_based'
            return rule_result

        # Step 2: Fallback to LLM if available
        if self.llm_backend:
            logger.info(f"Rule confidence {rule_result['confidence']} < {self.confidence_threshold}, using LLM fallback")

            llm_result = await self.llm_backend.process(prompt, params)
            llm_result['strategy'] = 'llm_fallback'
            llm_result['rule_result'] = rule_result['response']
            return llm_result

        # No LLM available, return rule result
        rule_result['strategy'] = 'rule_based_only'
        return rule_result


class BackendRegistry:
    """Registry of available processing backends."""

    def __init__(self):
        """Initialize backend registry."""
        self.backends: Dict[str, ProcessingBackend] = {}

    def register(self, backend: ProcessingBackend):
        """Register a backend."""
        self.backends[backend.backend_id] = backend
        logger.info(f"Registered backend: {backend.backend_id}")

    def get(self, backend_id: str) -> Optional[ProcessingBackend]:
        """Get backend by ID."""
        return self.backends.get(backend_id)

    def list_backends(self) -> list:
        """List all registered backends."""
        return list(self.backends.keys())


# Global registry
_registry = BackendRegistry()


def get_backend_registry() -> BackendRegistry:
    """Get global backend registry."""
    return _registry


def initialize_default_backends(
    openai_api_key: Optional[str] = None,
    ollama_url: str = "http://localhost:11434"
):
    """
    Initialize default backends.

    Args:
        openai_api_key: OpenAI API key (optional)
        ollama_url: Ollama server URL
    """
    registry = get_backend_registry()

    # Register rule-based backends (always available)
    registry.register(RuleBasedBackend("rules:classifier"))
    registry.register(RuleBasedBackend("rules:pii-detector"))
    registry.register(RuleBasedBackend("rules:injection-detector"))

    # Register Ollama (if available)
    try:
        registry.register(OllamaBackend("ollama:llama2", base_url=ollama_url, model="llama2"))
        logger.info("Ollama backend registered")
    except Exception as e:
        logger.warning(f"Could not register Ollama backend: {e}")

    # Register OpenAI (if API key provided)
    if openai_api_key:
        try:
            registry.register(OpenAIBackend("openai:gpt-3.5-turbo", api_key=openai_api_key, model="gpt-3.5-turbo"))
            registry.register(OpenAIBackend("openai:gpt-4", api_key=openai_api_key, model="gpt-4"))
            logger.info("OpenAI backends registered")
        except Exception as e:
            logger.warning(f"Could not register OpenAI backends: {e}")

    # Register hybrid backend
    rule_backend = RuleBasedBackend("rules:classifier")
    llm_backend = registry.get("ollama:llama2") or registry.get("openai:gpt-3.5-turbo")

    if llm_backend:
        registry.register(HybridBackend("hybrid:rule-llm", rule_backend, llm_backend))
        logger.info("Hybrid backend registered")
