"""
Collectors for local LLM servers (Ollama, LM Studio, LocalAI, etc.)
"""
import time
import uuid
import httpx
from typing import Any, Dict, Optional, List
from datetime import datetime
import asyncio

from models import AIEvent, EventType, Provider, TokenUsage, RiskLevel


class OllamaCollector:
    """
    Collector for Ollama local LLM.

    Ollama API: http://localhost:11434

    Usage:
        collector = OllamaCollector(
            base_url="http://localhost:11434",
            event_handler=my_handler
        )

        response = await collector.generate(
            model="llama2",
            prompt="Hello, how are you?"
        )
    """

    def __init__(self, base_url: str = "http://localhost:11434",
                 event_handler=None, user_id: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.event_handler = event_handler
        self.user_id = user_id
        self.session_id = str(uuid.uuid4())
        self.client = httpx.AsyncClient(timeout=300.0)  # 5 min timeout for local models

    async def generate(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate completion with monitoring."""
        event_id = str(uuid.uuid4())
        start_time = time.time()

        try:
            # Call Ollama API
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    **kwargs
                }
            )
            response.raise_for_status()
            result = response.json()

            # Calculate metrics
            latency_ms = (time.time() - start_time) * 1000

            # Extract response
            content = result.get("response", "")

            # Estimate tokens (Ollama doesn't always return exact counts)
            # Use eval_count if available, otherwise estimate
            prompt_tokens = result.get("prompt_eval_count", len(prompt.split()) * 1.3)
            completion_tokens = result.get("eval_count", len(content.split()) * 1.3)

            tokens = TokenUsage(
                prompt_tokens=int(prompt_tokens),
                completion_tokens=int(completion_tokens),
                total_tokens=int(prompt_tokens + completion_tokens)
            )

            # Local models = no cost
            cost_usd = 0.0

            # Create event
            event = AIEvent(
                id=event_id,
                event_type=EventType.RESPONSE,
                timestamp=datetime.utcnow(),
                provider=Provider.CUSTOM,
                model=model,
                prompt=prompt,
                prompt_length=len(prompt),
                response=content,
                response_length=len(content),
                latency_ms=latency_ms,
                tokens=tokens,
                cost_usd=cost_usd,
                success=True,
                user_id=self.user_id,
                session_id=self.session_id,
                metadata={
                    'total_duration': result.get('total_duration'),
                    'load_duration': result.get('load_duration'),
                    'eval_duration': result.get('eval_duration'),
                    'context': result.get('context'),
                    'provider': 'ollama'
                }
            )

            # Emit event
            if self.event_handler:
                if asyncio.iscoroutinefunction(self.event_handler):
                    await self.event_handler(event)
                else:
                    self.event_handler(event)

            return result

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000

            # Error event
            event = AIEvent(
                id=event_id,
                event_type=EventType.ERROR,
                timestamp=datetime.utcnow(),
                provider=Provider.CUSTOM,
                model=model,
                prompt=prompt,
                prompt_length=len(prompt),
                latency_ms=latency_ms,
                success=False,
                error_message=str(e),
                risk_level=RiskLevel.HIGH,
                user_id=self.user_id,
                session_id=self.session_id,
                metadata={'provider': 'ollama'}
            )

            if self.event_handler:
                if asyncio.iscoroutinefunction(self.event_handler):
                    await self.event_handler(event)
                else:
                    self.event_handler(event)

            raise

    async def chat(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Chat completion with monitoring."""
        event_id = str(uuid.uuid4())
        start_time = time.time()

        # Convert messages to prompt
        prompt = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in messages
        ])

        try:
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    **kwargs
                }
            )
            response.raise_for_status()
            result = response.json()

            latency_ms = (time.time() - start_time) * 1000

            # Extract response
            message = result.get("message", {})
            content = message.get("content", "")

            # Token estimation
            prompt_tokens = result.get("prompt_eval_count", len(prompt.split()) * 1.3)
            completion_tokens = result.get("eval_count", len(content.split()) * 1.3)

            tokens = TokenUsage(
                prompt_tokens=int(prompt_tokens),
                completion_tokens=int(completion_tokens),
                total_tokens=int(prompt_tokens + completion_tokens)
            )

            event = AIEvent(
                id=event_id,
                event_type=EventType.RESPONSE,
                timestamp=datetime.utcnow(),
                provider=Provider.CUSTOM,
                model=model,
                prompt=prompt,
                prompt_length=len(prompt),
                response=content,
                response_length=len(content),
                latency_ms=latency_ms,
                tokens=tokens,
                cost_usd=0.0,
                success=True,
                user_id=self.user_id,
                session_id=self.session_id,
                metadata={
                    'total_duration': result.get('total_duration'),
                    'provider': 'ollama',
                    'role': message.get('role')
                }
            )

            if self.event_handler:
                if asyncio.iscoroutinefunction(self.event_handler):
                    await self.event_handler(event)
                else:
                    self.event_handler(event)

            return result

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000

            event = AIEvent(
                id=event_id,
                event_type=EventType.ERROR,
                timestamp=datetime.utcnow(),
                provider=Provider.CUSTOM,
                model=model,
                prompt=prompt,
                prompt_length=len(prompt),
                latency_ms=latency_ms,
                success=False,
                error_message=str(e),
                risk_level=RiskLevel.HIGH,
                user_id=self.user_id,
                session_id=self.session_id,
                metadata={'provider': 'ollama'}
            )

            if self.event_handler:
                if asyncio.iscoroutinefunction(self.event_handler):
                    await self.event_handler(event)
                else:
                    self.event_handler(event)

            raise

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


class LMStudioCollector:
    """
    Collector for LM Studio local server.

    LM Studio runs OpenAI-compatible API on http://localhost:1234

    Usage:
        collector = LMStudioCollector(
            base_url="http://localhost:1234",
            event_handler=my_handler
        )

        response = await collector.chat_completion(
            model="local-model",
            messages=[{"role": "user", "content": "Hello!"}]
        )
    """

    def __init__(self, base_url: str = "http://localhost:1234",
                 event_handler=None, user_id: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.event_handler = event_handler
        self.user_id = user_id
        self.session_id = str(uuid.uuid4())
        self.client = httpx.AsyncClient(timeout=300.0)

    async def chat_completion(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """OpenAI-compatible chat completion."""
        event_id = str(uuid.uuid4())
        start_time = time.time()

        prompt = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in messages
        ])

        try:
            response = await self.client.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": model,
                    "messages": messages,
                    **kwargs
                }
            )
            response.raise_for_status()
            result = response.json()

            latency_ms = (time.time() - start_time) * 1000

            # Extract response (OpenAI format)
            choice = result.get("choices", [{}])[0]
            message = choice.get("message", {})
            content = message.get("content", "")

            # Token usage
            usage = result.get("usage", {})
            tokens = TokenUsage(
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0)
            )

            event = AIEvent(
                id=event_id,
                event_type=EventType.RESPONSE,
                timestamp=datetime.utcnow(),
                provider=Provider.CUSTOM,
                model=model,
                prompt=prompt,
                prompt_length=len(prompt),
                response=content,
                response_length=len(content),
                latency_ms=latency_ms,
                tokens=tokens,
                cost_usd=0.0,  # Local = free
                success=True,
                user_id=self.user_id,
                session_id=self.session_id,
                metadata={
                    'provider': 'lm_studio',
                    'finish_reason': choice.get('finish_reason')
                }
            )

            if self.event_handler:
                if asyncio.iscoroutinefunction(self.event_handler):
                    await self.event_handler(event)
                else:
                    self.event_handler(event)

            return result

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000

            event = AIEvent(
                id=event_id,
                event_type=EventType.ERROR,
                timestamp=datetime.utcnow(),
                provider=Provider.CUSTOM,
                model=model,
                prompt=prompt,
                prompt_length=len(prompt),
                latency_ms=latency_ms,
                success=False,
                error_message=str(e),
                risk_level=RiskLevel.HIGH,
                user_id=self.user_id,
                session_id=self.session_id,
                metadata={'provider': 'lm_studio'}
            )

            if self.event_handler:
                if asyncio.iscoroutinefunction(self.event_handler):
                    await self.event_handler(event)
                else:
                    self.event_handler(event)

            raise

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


class LocalAICollector:
    """
    Collector for LocalAI server.

    LocalAI is OpenAI-compatible: http://localhost:8080

    Usage:
        collector = LocalAICollector(
            base_url="http://localhost:8080",
            event_handler=my_handler
        )
    """

    def __init__(self, base_url: str = "http://localhost:8080",
                 event_handler=None, user_id: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.event_handler = event_handler
        self.user_id = user_id
        self.session_id = str(uuid.uuid4())
        self.client = httpx.AsyncClient(timeout=300.0)

    async def chat_completion(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """OpenAI-compatible chat completion."""
        # Same implementation as LM Studio (both OpenAI-compatible)
        event_id = str(uuid.uuid4())
        start_time = time.time()

        prompt = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in messages
        ])

        try:
            response = await self.client.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": model,
                    "messages": messages,
                    **kwargs
                }
            )
            response.raise_for_status()
            result = response.json()

            latency_ms = (time.time() - start_time) * 1000

            choice = result.get("choices", [{}])[0]
            message = choice.get("message", {})
            content = message.get("content", "")

            usage = result.get("usage", {})
            tokens = TokenUsage(
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0)
            )

            event = AIEvent(
                id=event_id,
                event_type=EventType.RESPONSE,
                timestamp=datetime.utcnow(),
                provider=Provider.CUSTOM,
                model=model,
                prompt=prompt,
                prompt_length=len(prompt),
                response=content,
                response_length=len(content),
                latency_ms=latency_ms,
                tokens=tokens,
                cost_usd=0.0,
                success=True,
                user_id=self.user_id,
                session_id=self.session_id,
                metadata={
                    'provider': 'localai',
                    'finish_reason': choice.get('finish_reason')
                }
            )

            if self.event_handler:
                if asyncio.iscoroutinefunction(self.event_handler):
                    await self.event_handler(event)
                else:
                    self.event_handler(event)

            return result

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000

            event = AIEvent(
                id=event_id,
                event_type=EventType.ERROR,
                timestamp=datetime.utcnow(),
                provider=Provider.CUSTOM,
                model=model,
                prompt=prompt,
                prompt_length=len(prompt),
                latency_ms=latency_ms,
                success=False,
                error_message=str(e),
                risk_level=RiskLevel.HIGH,
                user_id=self.user_id,
                session_id=self.session_id,
                metadata={'provider': 'localai'}
            )

            if self.event_handler:
                if asyncio.iscoroutinefunction(self.event_handler):
                    await self.event_handler(event)
                else:
                    self.event_handler(event)

            raise

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
