"""
Collectors - interceptors for AI API calls.
"""
import time
import uuid
from typing import Any, Dict, Optional
from datetime import datetime
import asyncio

from models import AIEvent, EventType, Provider, TokenUsage, RiskLevel


class BaseCollector:
    """Base collector with monitoring capabilities."""

    def __init__(self, event_handler=None):
        self.event_handler = event_handler

    async def emit_event(self, event: AIEvent):
        """Emit event to handler."""
        if self.event_handler:
            if asyncio.iscoroutinefunction(self.event_handler):
                await self.event_handler(event)
            else:
                self.event_handler(event)


class OpenAICollector(BaseCollector):
    """
    OpenAI API collector - wraps OpenAI client.

    Usage:
        from openai import OpenAI
        client = OpenAI()
        monitored_client = OpenAICollector(client, event_handler=my_handler)
        response = await monitored_client.chat.completions.create(...)
    """

    def __init__(self, openai_client, event_handler=None, user_id: Optional[str] = None):
        super().__init__(event_handler)
        self.client = openai_client
        self.user_id = user_id
        self.session_id = str(uuid.uuid4())

        # Wrap the completions create method
        self._wrap_chat_completions()

    def _wrap_chat_completions(self):
        """Wrap OpenAI chat completions method."""
        original_create = self.client.chat.completions.create

        def monitored_create(*args, **kwargs):
            return self._monitored_chat_completion(original_create, *args, **kwargs)

        self.client.chat.completions.create = monitored_create

    def _monitored_chat_completion(self, original_func, *args, **kwargs):
        """Monitor a chat completion call."""
        event_id = str(uuid.uuid4())
        start_time = time.time()

        # Extract request data
        messages = kwargs.get('messages', [])
        model = kwargs.get('model', 'unknown')

        # Combine messages into prompt
        prompt = "\n".join([
            f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
            for msg in messages
        ])

        try:
            # Call original function
            response = original_func(*args, **kwargs)

            # Calculate metrics
            latency_ms = (time.time() - start_time) * 1000

            # Extract response data
            choice = response.choices[0]
            content = choice.message.content
            finish_reason = choice.finish_reason

            # Token usage
            usage = response.usage
            tokens = TokenUsage(
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens
            )

            # Calculate cost (simplified pricing)
            cost_usd = self._calculate_openai_cost(model, tokens)

            # Create event
            event = AIEvent(
                id=event_id,
                event_type=EventType.RESPONSE,
                timestamp=datetime.utcnow(),
                provider=Provider.OPENAI,
                model=model,
                prompt=prompt,
                prompt_length=len(prompt),
                response=content,
                response_length=len(content) if content else 0,
                latency_ms=latency_ms,
                tokens=tokens,
                cost_usd=cost_usd,
                success=True,
                user_id=self.user_id,
                session_id=self.session_id,
                metadata={
                    'finish_reason': finish_reason,
                    'temperature': kwargs.get('temperature'),
                    'max_tokens': kwargs.get('max_tokens')
                }
            )

            # Emit event asynchronously if possible
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(self.emit_event(event))
            except RuntimeError:
                # No event loop, emit synchronously
                if self.event_handler:
                    self.event_handler(event)

            return response

        except Exception as e:
            # Error event
            latency_ms = (time.time() - start_time) * 1000

            event = AIEvent(
                id=event_id,
                event_type=EventType.ERROR,
                timestamp=datetime.utcnow(),
                provider=Provider.OPENAI,
                model=model,
                prompt=prompt,
                prompt_length=len(prompt),
                latency_ms=latency_ms,
                success=False,
                error_message=str(e),
                risk_level=RiskLevel.HIGH,
                user_id=self.user_id,
                session_id=self.session_id
            )

            try:
                loop = asyncio.get_event_loop()
                loop.create_task(self.emit_event(event))
            except RuntimeError:
                if self.event_handler:
                    self.event_handler(event)

            raise

    def _calculate_openai_cost(self, model: str, tokens: TokenUsage) -> float:
        """Calculate cost based on model and tokens."""
        # Simplified pricing (as of 2024)
        pricing = {
            'gpt-4': {'prompt': 0.03, 'completion': 0.06},
            'gpt-4-turbo': {'prompt': 0.01, 'completion': 0.03},
            'gpt-3.5-turbo': {'prompt': 0.0005, 'completion': 0.0015},
        }

        # Find matching pricing
        model_pricing = None
        for key in pricing:
            if key in model.lower():
                model_pricing = pricing[key]
                break

        if not model_pricing:
            model_pricing = pricing['gpt-3.5-turbo']  # default

        # Calculate cost per 1K tokens
        prompt_cost = (tokens.prompt_tokens / 1000) * model_pricing['prompt']
        completion_cost = (tokens.completion_tokens / 1000) * model_pricing['completion']

        return prompt_cost + completion_cost


class AnthropicCollector(BaseCollector):
    """
    Anthropic API collector - wraps Anthropic client.

    Usage:
        from anthropic import Anthropic
        client = Anthropic()
        monitored_client = AnthropicCollector(client, event_handler=my_handler)
        response = monitored_client.messages.create(...)
    """

    def __init__(self, anthropic_client, event_handler=None, user_id: Optional[str] = None):
        super().__init__(event_handler)
        self.client = anthropic_client
        self.user_id = user_id
        self.session_id = str(uuid.uuid4())

        # Wrap the messages create method
        self._wrap_messages()

    def _wrap_messages(self):
        """Wrap Anthropic messages method."""
        original_create = self.client.messages.create

        def monitored_create(*args, **kwargs):
            return self._monitored_message_create(original_create, *args, **kwargs)

        self.client.messages.create = monitored_create

    def _monitored_message_create(self, original_func, *args, **kwargs):
        """Monitor a message creation call."""
        event_id = str(uuid.uuid4())
        start_time = time.time()

        # Extract request data
        messages = kwargs.get('messages', [])
        model = kwargs.get('model', 'unknown')
        system = kwargs.get('system', '')

        # Combine into prompt
        prompt = f"System: {system}\n" if system else ""
        prompt += "\n".join([
            f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
            for msg in messages
        ])

        try:
            # Call original function
            response = original_func(*args, **kwargs)

            # Calculate metrics
            latency_ms = (time.time() - start_time) * 1000

            # Extract response data
            content = response.content[0].text if response.content else ""
            finish_reason = response.stop_reason

            # Token usage
            tokens = TokenUsage(
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens
            )

            # Calculate cost
            cost_usd = self._calculate_anthropic_cost(model, tokens)

            # Create event
            event = AIEvent(
                id=event_id,
                event_type=EventType.RESPONSE,
                timestamp=datetime.utcnow(),
                provider=Provider.ANTHROPIC,
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
                    'finish_reason': finish_reason,
                    'temperature': kwargs.get('temperature'),
                    'max_tokens': kwargs.get('max_tokens')
                }
            )

            try:
                loop = asyncio.get_event_loop()
                loop.create_task(self.emit_event(event))
            except RuntimeError:
                if self.event_handler:
                    self.event_handler(event)

            return response

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000

            event = AIEvent(
                id=event_id,
                event_type=EventType.ERROR,
                timestamp=datetime.utcnow(),
                provider=Provider.ANTHROPIC,
                model=model,
                prompt=prompt,
                prompt_length=len(prompt),
                latency_ms=latency_ms,
                success=False,
                error_message=str(e),
                risk_level=RiskLevel.HIGH,
                user_id=self.user_id,
                session_id=self.session_id
            )

            try:
                loop = asyncio.get_event_loop()
                loop.create_task(self.emit_event(event))
            except RuntimeError:
                if self.event_handler:
                    self.event_handler(event)

            raise

    def _calculate_anthropic_cost(self, model: str, tokens: TokenUsage) -> float:
        """Calculate cost based on model and tokens."""
        # Simplified pricing
        pricing = {
            'claude-3-opus': {'prompt': 0.015, 'completion': 0.075},
            'claude-3-sonnet': {'prompt': 0.003, 'completion': 0.015},
            'claude-3-haiku': {'prompt': 0.00025, 'completion': 0.00125},
        }

        model_pricing = None
        for key in pricing:
            if key in model.lower():
                model_pricing = pricing[key]
                break

        if not model_pricing:
            model_pricing = pricing['claude-3-haiku']  # default

        prompt_cost = (tokens.prompt_tokens / 1000) * model_pricing['prompt']
        completion_cost = (tokens.completion_tokens / 1000) * model_pricing['completion']

        return prompt_cost + completion_cost
