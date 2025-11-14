"""
Authentication and Authorization for MPC Server.

Implements short-lived tokens, signature verification, and RBAC/ABAC.
"""
import hashlib
import hmac
import jwt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class Permission(str, Enum):
    """Permission types."""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"
    PII_ACCESS = "pii_access"
    SENSITIVE_ACCESS = "sensitive_access"


class Role(str, Enum):
    """User roles."""
    USER = "user"
    SERVICE = "service"
    ADMIN = "admin"
    SYSTEM = "system"


@dataclass
class Principal:
    """Authenticated principal (user or service)."""
    client_id: str
    role: Role
    permissions: List[Permission]
    application_id: Optional[str] = None
    metadata: Dict[str, Any] = None

    def has_permission(self, permission: Permission) -> bool:
        """Check if principal has permission."""
        return permission in self.permissions or Permission.ADMIN in self.permissions


class TokenManager:
    """
    Manages JWT tokens with short TTL.

    Tokens are signed and include:
    - client_id
    - role
    - permissions
    - exp (expiration)
    - iat (issued at)
    """

    def __init__(self, secret_key: str, token_ttl_minutes: int = 15):
        """
        Initialize token manager.

        Args:
            secret_key: Secret key for signing tokens (should be from KMS)
            token_ttl_minutes: Token time-to-live in minutes
        """
        self.secret_key = secret_key
        self.token_ttl_minutes = token_ttl_minutes
        self.algorithm = "HS256"

    def create_token(
        self,
        client_id: str,
        role: Role,
        permissions: List[Permission],
        application_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new JWT token.

        Args:
            client_id: Client identifier
            role: Client role
            permissions: List of permissions
            application_id: Optional application identifier
            metadata: Optional additional metadata

        Returns:
            JWT token string
        """
        now = datetime.utcnow()
        exp = now + timedelta(minutes=self.token_ttl_minutes)

        payload = {
            'client_id': client_id,
            'role': role.value,
            'permissions': [p.value for p in permissions],
            'iat': int(now.timestamp()),
            'exp': int(exp.timestamp()),
            'jti': secrets.token_hex(16),  # JWT ID for tracking
        }

        if application_id:
            payload['application_id'] = application_id

        if metadata:
            payload['metadata'] = metadata

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def verify_token(self, token: str) -> Optional[Principal]:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token string

        Returns:
            Principal if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={'verify_exp': True}
            )

            return Principal(
                client_id=payload['client_id'],
                role=Role(payload['role']),
                permissions=[Permission(p) for p in payload['permissions']],
                application_id=payload.get('application_id'),
                metadata=payload.get('metadata', {})
            )

        except jwt.ExpiredSignatureError:
            # Token expired
            return None
        except jwt.InvalidTokenError:
            # Invalid token
            return None


class SignatureVerifier:
    """
    Verifies HMAC signatures for request integrity.

    Ensures that the request payload hasn't been tampered with.
    """

    def __init__(self, shared_secret: str):
        """
        Initialize signature verifier.

        Args:
            shared_secret: Shared secret for HMAC (should be from KMS)
        """
        self.shared_secret = shared_secret.encode()

    def sign(self, payload: str) -> str:
        """
        Create HMAC signature for payload.

        Args:
            payload: Payload to sign (typically JSON string)

        Returns:
            Hex-encoded signature
        """
        signature = hmac.new(
            self.shared_secret,
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    def verify(self, payload: str, signature: str) -> bool:
        """
        Verify HMAC signature.

        Args:
            payload: Original payload
            signature: Signature to verify

        Returns:
            True if valid, False otherwise
        """
        expected_signature = self.sign(payload)
        return hmac.compare_digest(expected_signature, signature)


class AuthorizationPolicy:
    """
    Authorization policy engine for RBAC/ABAC.

    Determines if a principal is allowed to perform an action
    on a resource with given attributes.
    """

    def __init__(self):
        """Initialize authorization policy."""
        # Default policies
        self.policies = self._default_policies()

    def _default_policies(self) -> Dict[str, Any]:
        """Default authorization policies."""
        return {
            'sensitivity_access': {
                # Role -> allowed sensitivity levels
                Role.USER: ['public', 'internal'],
                Role.SERVICE: ['public', 'internal', 'sensitive'],
                Role.ADMIN: ['public', 'internal', 'sensitive', 'pii', 'confidential'],
                Role.SYSTEM: ['public', 'internal', 'sensitive', 'pii', 'confidential'],
            },
            'processing_hints': {
                # Role -> allowed processing hints
                Role.USER: ['auto', 'model:small', 'rule:engine'],
                Role.SERVICE: ['auto', 'model:small', 'model:large', 'rule:engine', 'hybrid'],
                Role.ADMIN: ['auto', 'model:small', 'model:large', 'model:private', 'rule:engine', 'hybrid'],
                Role.SYSTEM: ['auto', 'model:small', 'model:large', 'model:private', 'rule:engine', 'hybrid'],
            },
            'max_cost_per_request': {
                # Role -> max cost in USD
                Role.USER: 0.10,
                Role.SERVICE: 1.00,
                Role.ADMIN: 10.00,
                Role.SYSTEM: 100.00,
            }
        }

    def is_authorized(
        self,
        principal: Principal,
        action: str,
        resource_attributes: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        Check if principal is authorized to perform action on resource.

        Args:
            principal: Authenticated principal
            action: Action to perform (e.g., 'process', 'query')
            resource_attributes: Attributes of the resource (e.g., sensitivity, cost)

        Returns:
            Tuple of (is_authorized, reason)
        """
        # Check sensitivity access
        sensitivity = resource_attributes.get('sensitivity', 'internal')
        allowed_sensitivities = self.policies['sensitivity_access'].get(principal.role, [])

        if sensitivity not in allowed_sensitivities:
            return False, f"Role '{principal.role.value}' not allowed to access '{sensitivity}' data"

        # Check PII access permission for sensitive/pii data
        if sensitivity in ['sensitive', 'pii', 'confidential']:
            if not principal.has_permission(Permission.PII_ACCESS):
                return False, f"Permission '{Permission.PII_ACCESS.value}' required for '{sensitivity}' data"

        # Check processing hint authorization
        processing_hint = resource_attributes.get('processing_hint')
        if processing_hint:
            allowed_hints = self.policies['processing_hints'].get(principal.role, [])
            if processing_hint not in allowed_hints:
                return False, f"Role '{principal.role.value}' not allowed to use processing hint '{processing_hint}'"

        # Check cost limits
        estimated_cost = resource_attributes.get('estimated_cost', 0)
        max_cost = self.policies['max_cost_per_request'].get(principal.role, 0)
        if estimated_cost > max_cost:
            return False, f"Estimated cost ${estimated_cost:.4f} exceeds limit ${max_cost:.4f} for role '{principal.role.value}'"

        return True, None

    def add_policy(self, policy_name: str, policy: Dict[str, Any]):
        """Add or update a policy."""
        self.policies[policy_name] = policy

    def get_policy(self, policy_name: str) -> Optional[Dict[str, Any]]:
        """Get a policy by name."""
        return self.policies.get(policy_name)


class AccessControl:
    """
    Complete access control system combining authentication and authorization.
    """

    def __init__(
        self,
        jwt_secret: str,
        hmac_secret: str,
        token_ttl_minutes: int = 15
    ):
        """
        Initialize access control.

        Args:
            jwt_secret: Secret for JWT signing
            hmac_secret: Secret for HMAC signatures
            token_ttl_minutes: Token TTL in minutes
        """
        self.token_manager = TokenManager(jwt_secret, token_ttl_minutes)
        self.signature_verifier = SignatureVerifier(hmac_secret)
        self.authz_policy = AuthorizationPolicy()

    def authenticate(self, token: str) -> Optional[Principal]:
        """
        Authenticate using JWT token.

        Args:
            token: JWT token

        Returns:
            Principal if authenticated, None otherwise
        """
        return self.token_manager.verify_token(token)

    def verify_signature(self, payload: str, signature: str) -> bool:
        """
        Verify request signature.

        Args:
            payload: Request payload
            signature: HMAC signature

        Returns:
            True if valid
        """
        return self.signature_verifier.verify(payload, signature)

    def authorize(
        self,
        principal: Principal,
        action: str,
        resource_attributes: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        Authorize action.

        Args:
            principal: Authenticated principal
            action: Action to perform
            resource_attributes: Resource attributes

        Returns:
            Tuple of (is_authorized, reason)
        """
        return self.authz_policy.is_authorized(principal, action, resource_attributes)

    def create_service_token(
        self,
        service_name: str,
        permissions: List[Permission]
    ) -> str:
        """
        Create a service token.

        Args:
            service_name: Service identifier
            permissions: List of permissions

        Returns:
            JWT token
        """
        return self.token_manager.create_token(
            client_id=service_name,
            role=Role.SERVICE,
            permissions=permissions,
            application_id=service_name
        )
