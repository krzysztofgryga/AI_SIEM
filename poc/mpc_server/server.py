"""
MPC Server - Main Collection Layer Server.

The MPC Server orchestrates:
1. Request validation
2. Authentication & authorization
3. PII detection and routing
4. Intelligent backend selection
5. Request forwarding to processing layer
6. Response aggregation
7. Audit logging
"""
import uuid
import time
from datetime import datetime
from typing import Optional, Dict, Any
import logging

from schemas.contracts import (
    MPCRequest,
    MPCResponse,
    ResponseStatus,
    ProcessingInfo,
    ErrorInfo,
    SensitivityLevel,
    validate_payload
)
from security.auth import AccessControl, Permission, Role
from security.pii_handler import PIIDetector, PIIRedactor, PIIRouter
from security.audit import AuditLogger, Outcome
from mpc_server.router import (
    IntelligentRouter,
    CapabilityType,
    get_default_backends
)


logger = logging.getLogger(__name__)


class MPCServer:
    """
    MPC (Multi-Provider Coordinator) Server.

    Acts as intelligent middleware between Application Layer and Processing Layer.
    """

    def __init__(
        self,
        jwt_secret: str = "your-jwt-secret-here",  # Should come from KMS
        hmac_secret: str = "your-hmac-secret-here",  # Should come from KMS
        enable_pii_detection: bool = True,
        enable_audit: bool = True,
        audit_log_file: str = "mpc_audit.log"
    ):
        """
        Initialize MPC Server.

        Args:
            jwt_secret: Secret for JWT tokens
            hmac_secret: Secret for HMAC signatures
            enable_pii_detection: Enable PII detection
            enable_audit: Enable audit logging
            audit_log_file: Audit log file path
        """
        # Security components
        self.access_control = AccessControl(jwt_secret, hmac_secret)

        # PII components
        self.pii_detector = PIIDetector() if enable_pii_detection else None
        self.pii_redactor = PIIRedactor(strategy="TOKENIZE")
        self.pii_router = PIIRouter()

        # Routing
        self.router = IntelligentRouter(get_default_backends())

        # Audit
        self.audit = AuditLogger(log_file=audit_log_file) if enable_audit else None

        logger.info("MPC Server initialized")

    async def process_request(self, request: MPCRequest) -> MPCResponse:
        """
        Process incoming request.

        Pipeline:
        1. Validate request schema
        2. Authenticate & authorize
        3. Detect PII
        4. Route to appropriate backend
        5. Forward to processing layer
        6. Return response

        Args:
            request: MPC request

        Returns:
            MPC response
        """
        start_time = time.time()

        try:
            # Step 1: Validate payload schema
            try:
                validated_payload = validate_payload(
                    request.payload_schema,
                    request.payload
                )
            except ValueError as e:
                return self._error_response(
                    request,
                    "schema_validation_failed",
                    f"Invalid payload schema: {str(e)}"
                )

            # Step 2: Authenticate
            principal = self.access_control.authenticate(request.auth.token)
            if not principal:
                if self.audit:
                    self.audit.log_authorization(
                        request.request_id,
                        "unknown",
                        "process",
                        is_authorized=False,
                        reason="Invalid or expired token"
                    )

                return self._error_response(
                    request,
                    "authentication_failed",
                    "Invalid or expired authentication token"
                )

            # Step 3: Verify signature if provided
            if request.auth.signature:
                payload_str = request.payload.__str__()
                if not self.access_control.verify_signature(payload_str, request.auth.signature):
                    return self._error_response(
                        request,
                        "signature_verification_failed",
                        "Request signature verification failed"
                    )

            # Step 4: Authorize
            resource_attributes = {
                'sensitivity': request.config.sensitivity.value,
                'processing_hint': request.config.processing_hint.value,
                'estimated_cost': 0.01,  # Initial estimate
            }

            is_authorized, reason = self.access_control.authorize(
                principal,
                "process",
                resource_attributes
            )

            if not is_authorized:
                if self.audit:
                    self.audit.log_authorization(
                        request.request_id,
                        principal.client_id,
                        "process",
                        is_authorized=False,
                        reason=reason
                    )

                return self._error_response(
                    request,
                    "authorization_failed",
                    reason or "Not authorized"
                )

            if self.audit:
                self.audit.log_authorization(
                    request.request_id,
                    principal.client_id,
                    "process",
                    is_authorized=True
                )

            # Step 5: PII Detection
            security_flags = {}
            prompt_text = request.payload.get('prompt', '')

            if self.pii_detector and request.config.enable_pii_detection:
                pii_result = self.pii_detector.detect(prompt_text)

                if pii_result.has_pii:
                    security_flags['has_pii'] = True
                    security_flags['pii_types'] = [pt.value for pt in pii_result.pii_types]

                    if self.audit:
                        self.audit.log_pii_detection(
                            request.request_id,
                            [pt.value for pt in pii_result.pii_types],
                            "detected_and_logged"
                        )

                    # Check if backend allows PII
                    # This will be validated during routing

            # Step 6: PII-aware routing
            should_block, block_reason = self.pii_router.should_block(
                prompt_text,
                request.config.processing_hint.value
            )

            if should_block:
                if self.audit:
                    self.audit.log_security_violation(
                        request.request_id,
                        "pii_routing_violation",
                        {'reason': block_reason}
                    )

                return self._error_response(
                    request,
                    "pii_routing_blocked",
                    block_reason
                )

            # Step 7: Determine capability from request
            # For now, default to text generation
            # In production, this would be more sophisticated
            capability = self._infer_capability(request)

            # Step 8: Route request
            estimated_tokens = len(prompt_text.split()) * 1.5  # Rough estimate

            try:
                routing_decision = self.router.route(
                    capability=capability,
                    sensitivity=request.config.sensitivity,
                    processing_hint=request.config.processing_hint,
                    max_cost=1.0,  # Could come from principal's quota
                    max_latency_ms=request.config.timeout_ms,
                    estimated_tokens=int(estimated_tokens),
                    use_cascade=request.config.max_retries > 0
                )

                logger.info(
                    f"Routed request {request.request_id} to {routing_decision.backend_id} "
                    f"(fallbacks: {routing_decision.fallback_backends})"
                )

            except ValueError as e:
                return self._error_response(
                    request,
                    "routing_failed",
                    str(e)
                )

            # Step 9: Forward to processing layer
            # In a real implementation, this would call the actual processing backend
            # For now, we'll simulate a response
            processing_result = await self._forward_to_processing(
                request,
                routing_decision.backend_id,
                validated_payload
            )

            # Step 10: Build response
            latency_ms = (time.time() - start_time) * 1000

            if self.audit:
                self.audit.log_processing(
                    request.request_id,
                    routing_decision.backend_id,
                    Outcome.SUCCESS,
                    latency_ms=latency_ms,
                    cost_usd=processing_result.get('cost', 0.0)
                )

            return MPCResponse(
                request_id=request.request_id,
                status=ResponseStatus.OK,
                result=processing_result,
                processing=ProcessingInfo(
                    backend=routing_decision.backend_id,
                    latency_ms=latency_ms,
                    cost_usd=processing_result.get('cost', 0.0),
                    confidence=routing_decision.confidence,
                    fallback_used=False
                ),
                security_flags=security_flags
            )

        except Exception as e:
            logger.error(f"Error processing request {request.request_id}: {str(e)}", exc_info=True)

            if self.audit:
                self.audit.log_processing(
                    request.request_id,
                    "unknown",
                    Outcome.ERROR,
                    error=str(e)
                )

            return self._error_response(
                request,
                "internal_error",
                f"Internal server error: {str(e)}"
            )

    def _infer_capability(self, request: MPCRequest) -> CapabilityType:
        """
        Infer required capability from request.

        This is a simple heuristic. In production, this would be more sophisticated
        or explicitly provided in the request.
        """
        # Check payload schema
        if 'security' in request.payload_schema:
            return CapabilityType.SECURITY_SCAN

        if 'extract' in request.payload_schema:
            return CapabilityType.EXTRACTION

        if 'classify' in request.payload_schema:
            return CapabilityType.CLASSIFICATION

        # Default to text generation
        return CapabilityType.TEXT_GENERATION

    async def _forward_to_processing(
        self,
        request: MPCRequest,
        backend_id: str,
        payload: Any
    ) -> Dict[str, Any]:
        """
        Forward request to processing layer.

        In a real implementation, this would:
        1. Select the appropriate processing module based on backend_id
        2. Call the processing module
        3. Handle retries and fallbacks
        4. Aggregate results

        For now, this is a placeholder that returns a simulated response.
        """
        # Simulate processing
        # In production, this would actually call the backend

        # Extract relevant fields from payload
        if hasattr(payload, 'prompt'):
            prompt = payload.prompt
        else:
            prompt = str(payload)

        # Simulated response
        return {
            'response': f"Processed by {backend_id}: {prompt[:50]}...",
            'tokens': 150,
            'cost': 0.0023,
            'backend': backend_id
        }

    def _error_response(
        self,
        request: MPCRequest,
        error_code: str,
        error_message: str
    ) -> MPCResponse:
        """Create error response."""
        return MPCResponse(
            request_id=request.request_id,
            status=ResponseStatus.ERROR,
            error=ErrorInfo(
                code=error_code,
                message=error_message
            )
        )

    def health_check(self) -> Dict[str, Any]:
        """
        Health check endpoint.

        Returns:
            Health status
        """
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'components': {
                'router': 'ok',
                'pii_detector': 'ok' if self.pii_detector else 'disabled',
                'audit': 'ok' if self.audit else 'disabled',
            }
        }


class MPCServerConfig:
    """Configuration for MPC Server."""

    def __init__(
        self,
        jwt_secret: Optional[str] = None,
        hmac_secret: Optional[str] = None,
        enable_pii_detection: bool = True,
        enable_audit: bool = True,
        audit_log_file: str = "mpc_audit.log",
        max_request_size_bytes: int = 1024 * 1024,  # 1MB
        request_timeout_ms: int = 30000,
    ):
        """Initialize configuration."""
        self.jwt_secret = jwt_secret or self._generate_secret()
        self.hmac_secret = hmac_secret or self._generate_secret()
        self.enable_pii_detection = enable_pii_detection
        self.enable_audit = enable_audit
        self.audit_log_file = audit_log_file
        self.max_request_size_bytes = max_request_size_bytes
        self.request_timeout_ms = request_timeout_ms

    @staticmethod
    def _generate_secret() -> str:
        """Generate a random secret (for development only)."""
        import secrets
        return secrets.token_hex(32)
