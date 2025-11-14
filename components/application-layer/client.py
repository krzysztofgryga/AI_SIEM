"""
MPC Client - Application Layer client for interacting with MPC Server.
"""
from typing import Optional, Dict, Any
import httpx
import logging

from schemas.contracts import (
    MPCRequest,
    MPCResponse,
    SourceInfo,
    AuthInfo,
    ProcessingConfig,
    RequestType,
    SensitivityLevel,
    ProcessingHint,
    ReturnRoute
)


logger = logging.getLogger(__name__)


class MPCClient:
    """
    Client for MPC Server.

    This is the Application Layer component that communicates with
    the Collection Layer (MPC Server).
    """

    def __init__(
        self,
        mpc_server_url: str = "http://localhost:8000",
        application_id: str = "default-app",
        auth_token: str = "default-token",
        environment: str = "dev"
    ):
        """
        Initialize MPC client.

        Args:
            mpc_server_url: URL of MPC server
            application_id: Application identifier
            auth_token: Authentication token
            environment: Environment (dev, staging, prod)
        """
        self.mpc_server_url = mpc_server_url
        self.application_id = application_id
        self.auth_token = auth_token
        self.environment = environment

    async def process(
        self,
        prompt: str,
        model: str = "auto",
        sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL,
        processing_hint: ProcessingHint = ProcessingHint.AUTO,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        enable_pii_detection: bool = True,
        enable_injection_detection: bool = True,
        timeout_ms: int = 30000
    ) -> Dict[str, Any]:
        """
        Send a processing request to MPC server.

        Args:
            prompt: Input prompt
            model: Model to use (or "auto" for automatic selection)
            sensitivity: Data sensitivity level
            processing_hint: Processing hint for routing
            max_tokens: Maximum tokens to generate
            temperature: Temperature parameter
            enable_pii_detection: Enable PII detection
            enable_injection_detection: Enable injection detection
            timeout_ms: Request timeout in milliseconds

        Returns:
            Processing result
        """
        # Build request
        request = MPCRequest(
            source=SourceInfo(
                application_id=self.application_id,
                environment=self.environment
            ),
            type=RequestType.PROCESS_REQUEST,
            payload_schema="llm.request.v1",
            payload={
                "model": model,
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature
            },
            config=ProcessingConfig(
                sensitivity=sensitivity,
                processing_hint=processing_hint,
                return_route=ReturnRoute.SYNC,
                timeout_ms=timeout_ms,
                enable_pii_detection=enable_pii_detection,
                enable_injection_detection=enable_injection_detection
            ),
            auth=AuthInfo(
                token=self.auth_token
            )
        )

        # In a real HTTP implementation, you would send this request:
        # response = await httpx.post(f"{self.mpc_server_url}/process", json=request.dict())

        # For now, we'll simulate by directly calling MPC server
        from mpc_server.server import MPCServer

        mpc_server = MPCServer()
        response = await mpc_server.process_request(request)

        if response.status == "ok":
            return response.result
        else:
            raise Exception(f"MPC error: {response.error.message if response.error else 'Unknown error'}")

    async def batch_process(
        self,
        prompts: list[str],
        **kwargs
    ) -> list[Dict[str, Any]]:
        """
        Process multiple prompts in batch.

        Args:
            prompts: List of prompts
            **kwargs: Same as process()

        Returns:
            List of results
        """
        results = []
        for prompt in prompts:
            result = await self.process(prompt, **kwargs)
            results.append(result)

        return results

    async def health_check(self) -> Dict[str, Any]:
        """
        Check MPC server health.

        Returns:
            Health status
        """
        from mpc_server.server import MPCServer

        mpc_server = MPCServer()
        return mpc_server.health_check()


class SimpleMPCClient:
    """
    Simplified MPC client with sensible defaults.

    For users who just want to send prompts without dealing with all the configuration.
    """

    def __init__(
        self,
        auth_token: str = "default-token",
        application_id: str = "simple-app"
    ):
        """
        Initialize simple client.

        Args:
            auth_token: Authentication token
            application_id: Application identifier
        """
        self.client = MPCClient(
            auth_token=auth_token,
            application_id=application_id
        )

    async def ask(
        self,
        question: str,
        use_private_model: bool = False
    ) -> str:
        """
        Ask a question and get a response.

        Args:
            question: Question to ask
            use_private_model: Use private (on-prem) model

        Returns:
            Response text
        """
        hint = ProcessingHint.MODEL_PRIVATE if use_private_model else ProcessingHint.AUTO

        result = await self.client.process(
            prompt=question,
            processing_hint=hint,
            sensitivity=SensitivityLevel.INTERNAL
        )

        return result.get('response', '')

    async def ask_secure(
        self,
        question: str,
        contains_pii: bool = False
    ) -> str:
        """
        Ask a question with security considerations.

        Args:
            question: Question to ask
            contains_pii: Whether question contains PII

        Returns:
            Response text
        """
        sensitivity = SensitivityLevel.PII if contains_pii else SensitivityLevel.INTERNAL

        result = await self.client.process(
            prompt=question,
            processing_hint=ProcessingHint.MODEL_PRIVATE,  # Always use private for secure
            sensitivity=sensitivity,
            enable_pii_detection=True,
            enable_injection_detection=True
        )

        return result.get('response', '')
