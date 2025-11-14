"""
PII Handler - Detection, Redaction, and Tokenization.

Implements data minimization and PII-aware routing according to security best practices.
"""
import re
import hashlib
import secrets
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class PIIType(str, Enum):
    """Types of PII that can be detected."""
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    PASSPORT = "passport"
    IBAN = "iban"
    NAME = "name"  # Detected via patterns, not perfect
    ADDRESS = "address"


@dataclass
class PIIMatch:
    """A detected PII match."""
    pii_type: PIIType
    value: str
    start: int
    end: int
    confidence: float = 1.0


@dataclass
class PIIDetectionResult:
    """Result of PII detection."""
    has_pii: bool
    matches: List[PIIMatch]
    pii_types: List[PIIType]
    redacted_text: Optional[str] = None
    tokens: Optional[Dict[str, str]] = None  # original -> token mapping


class PIIDetector:
    """
    Detects PII in text using regex patterns.

    Patterns are based on common PII formats. For production use,
    consider using ML-based PII detection for better accuracy.
    """

    # Regex patterns for PII detection
    PATTERNS = {
        PIIType.EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        PIIType.PHONE: r'\b(?:\+?1[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b',
        PIIType.SSN: r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',
        PIIType.CREDIT_CARD: r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        PIIType.IP_ADDRESS: r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        PIIType.PASSPORT: r'\b[A-Z]{1,2}\d{6,9}\b',
        PIIType.IBAN: r'\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b',
    }

    def __init__(self):
        """Initialize PII detector with compiled patterns."""
        self.compiled_patterns = {
            pii_type: re.compile(pattern, re.IGNORECASE)
            for pii_type, pattern in self.PATTERNS.items()
        }

    def detect(self, text: str) -> PIIDetectionResult:
        """
        Detect PII in text.

        Args:
            text: Text to scan for PII

        Returns:
            PIIDetectionResult with all matches
        """
        matches: List[PIIMatch] = []

        for pii_type, pattern in self.compiled_patterns.items():
            for match in pattern.finditer(text):
                # Additional validation for specific types
                if pii_type == PIIType.CREDIT_CARD:
                    if not self._validate_credit_card(match.group()):
                        continue
                elif pii_type == PIIType.IP_ADDRESS:
                    if not self._validate_ip_address(match.group()):
                        continue

                matches.append(PIIMatch(
                    pii_type=pii_type,
                    value=match.group(),
                    start=match.start(),
                    end=match.end()
                ))

        pii_types = list(set([m.pii_type for m in matches]))

        return PIIDetectionResult(
            has_pii=len(matches) > 0,
            matches=matches,
            pii_types=pii_types
        )

    def _validate_credit_card(self, card_number: str) -> bool:
        """Validate credit card using Luhn algorithm."""
        digits = [int(d) for d in card_number if d.isdigit()]
        if len(digits) < 13 or len(digits) > 19:
            return False

        # Luhn algorithm
        checksum = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            checksum += digit

        return checksum % 10 == 0

    def _validate_ip_address(self, ip: str) -> bool:
        """Validate IP address format."""
        parts = ip.split('.')
        if len(parts) != 4:
            return False

        try:
            return all(0 <= int(part) <= 255 for part in parts)
        except ValueError:
            return False


class PIIRedactor:
    """
    Redacts or tokenizes PII in text.

    Supports multiple strategies:
    - REDACT: Replace with [REDACTED:{TYPE}]
    - MASK: Replace with asterisks (****)
    - HASH: Replace with hash of the value
    - TOKENIZE: Replace with reversible token (requires key management)
    """

    def __init__(self, strategy: str = "REDACT"):
        """
        Initialize redactor.

        Args:
            strategy: Redaction strategy (REDACT, MASK, HASH, TOKENIZE)
        """
        self.strategy = strategy
        self.detector = PIIDetector()
        self._token_map: Dict[str, str] = {}  # For tokenization
        self._reverse_map: Dict[str, str] = {}  # For de-tokenization

    def redact(self, text: str) -> Tuple[str, PIIDetectionResult]:
        """
        Redact PII from text.

        Args:
            text: Original text

        Returns:
            Tuple of (redacted_text, detection_result)
        """
        result = self.detector.detect(text)

        if not result.has_pii:
            return text, result

        # Sort matches by position (reverse order to maintain indices)
        sorted_matches = sorted(result.matches, key=lambda m: m.start, reverse=True)

        redacted_text = text
        tokens = {}

        for match in sorted_matches:
            replacement = self._get_replacement(match)
            redacted_text = (
                redacted_text[:match.start] +
                replacement +
                redacted_text[match.end:]
            )
            tokens[match.value] = replacement

        result.redacted_text = redacted_text
        result.tokens = tokens

        return redacted_text, result

    def _get_replacement(self, match: PIIMatch) -> str:
        """Get replacement string based on strategy."""
        if self.strategy == "REDACT":
            return f"[REDACTED:{match.pii_type.value.upper()}]"

        elif self.strategy == "MASK":
            return "****"

        elif self.strategy == "HASH":
            hashed = hashlib.sha256(match.value.encode()).hexdigest()[:8]
            return f"[{match.pii_type.value.upper()}:{hashed}]"

        elif self.strategy == "TOKENIZE":
            if match.value not in self._token_map:
                token = f"TOKEN_{secrets.token_hex(8)}"
                self._token_map[match.value] = token
                self._reverse_map[token] = match.value
            return self._token_map[match.value]

        else:
            return "[REDACTED]"

    def detokenize(self, text: str) -> str:
        """
        Reverse tokenization (only works with TOKENIZE strategy).

        Args:
            text: Tokenized text

        Returns:
            Original text
        """
        if self.strategy != "TOKENIZE":
            raise ValueError("Detokenization only available with TOKENIZE strategy")

        result = text
        for token, original in self._reverse_map.items():
            result = result.replace(token, original)

        return result


class PIIRouter:
    """
    Routes requests based on PII sensitivity.

    Implements PII-aware routing to ensure sensitive data
    only goes to approved backends.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize PII router.

        Args:
            config: Configuration for routing rules
        """
        self.config = config or {}
        self.detector = PIIDetector()

        # Default routing rules
        self.routing_rules = self.config.get('routing_rules', {
            'no_pii': ['public_model', 'cloud_model'],
            'has_pii': ['private_model', 'on_prem_model'],
            'sensitive_pii': ['on_prem_model_encrypted'],
        })

    def get_allowed_backends(self, text: str, sensitivity: str = "internal") -> List[str]:
        """
        Get list of allowed backends based on PII detection and sensitivity.

        Args:
            text: Text to analyze
            sensitivity: Sensitivity level (public, internal, sensitive, pii)

        Returns:
            List of allowed backend identifiers
        """
        result = self.detector.detect(text)

        # Determine routing category
        if not result.has_pii and sensitivity in ['public', 'internal']:
            return self.routing_rules.get('no_pii', [])

        elif result.has_pii and sensitivity in ['internal', 'sensitive']:
            return self.routing_rules.get('has_pii', [])

        else:  # High sensitivity or sensitive PII types
            return self.routing_rules.get('sensitive_pii', [])

    def should_block(self, text: str, backend: str) -> Tuple[bool, Optional[str]]:
        """
        Check if request should be blocked based on PII and backend.

        Args:
            text: Text to analyze
            backend: Target backend

        Returns:
            Tuple of (should_block, reason)
        """
        result = self.detector.detect(text)

        if not result.has_pii:
            return False, None

        # Check if backend is allowed for PII
        pii_allowed_backends = (
            self.routing_rules.get('has_pii', []) +
            self.routing_rules.get('sensitive_pii', [])
        )

        if backend not in pii_allowed_backends:
            return True, f"Backend '{backend}' not allowed for PII data. Detected: {result.pii_types}"

        # Check for sensitive PII types (SSN, Credit Card, Passport)
        sensitive_types = {PIIType.SSN, PIIType.CREDIT_CARD, PIIType.PASSPORT}
        if any(m.pii_type in sensitive_types for m in result.matches):
            secure_backends = self.routing_rules.get('sensitive_pii', [])
            if backend not in secure_backends:
                return True, f"Backend '{backend}' not allowed for sensitive PII (SSN/CC/Passport)"

        return False, None
