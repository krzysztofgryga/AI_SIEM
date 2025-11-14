# Security Components

**Komponenty Bezpieczeństwa** - Authentication, authorization, PII detection, audit logging.

## 📋 Opis

Security Layer dostarcza wszystkie funkcje bezpieczeństwa dla systemu AI SIEM:
- **Authentication**: JWT tokens
- **Authorization**: RBAC (Role-Based Access Control)
- **PII Detection**: Wykrywanie danych osobowych
- **PII Redaction**: Maskowanie danych osobowych
- **PII Routing**: Routing zapytań z PII do odpowiednich backendów
- **Audit Logging**: Pełny audit trail

## 🎯 Komponenty

### 1. Authentication & Authorization (`auth.py`)

#### `AccessControl`
Główny komponent auth:
```python
from security.auth import AccessControl, Role, Permission

# Inicjalizacja
ac = AccessControl(
    jwt_secret="your-jwt-secret",
    hmac_secret="your-hmac-secret"
)

# Tworzenie tokenów
token = ac.create_service_token(
    client_id="app-123",
    permissions=[Permission.READ, Permission.EXECUTE]
)

# Walidacja tokena
principal = ac.authenticate(token)
if principal:
    print(f"Authenticated: {principal.client_id}")

# Autoryzacja
is_authorized, reason = ac.authorize(
    principal,
    action="process",
    resource_attributes={'sensitivity': 'internal'}
)
```

#### Roles & Permissions
```python
class Role(str, Enum):
    ADMIN = "admin"           # Wszystkie uprawnienia
    SERVICE = "service"       # Read + Execute
    READ_ONLY = "read_only"   # Tylko odczyt

class Permission(str, Enum):
    READ = "read"             # Odczyt danych
    WRITE = "write"           # Zapis danych
    EXECUTE = "execute"       # Wykonywanie zapytań
    ADMIN = "admin"           # Administracja
```

### 2. PII Detection & Handling (`pii_handler.py`)

#### `PIIDetector`
Wykrywanie PII:
```python
from security.pii_handler import PIIDetector, PIIType

detector = PIIDetector()

# Wykryj PII w tekście
text = "My email is john@example.com and phone is 555-123-4567"
result = detector.detect(text)

if result.has_pii:
    print(f"Found PII: {result.pii_types}")
    for finding in result.findings:
        print(f"- {finding.pii_type}: {finding.value}")
```

Wykrywane typy PII:
```python
class PIIType(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"                    # US Social Security Number
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    DATE_OF_BIRTH = "date_of_birth"
```

#### `PIIRedactor`
Maskowanie PII:
```python
from security.pii_handler import PIIRedactor

redactor = PIIRedactor(strategy="MASK")  # lub "TOKENIZE", "REMOVE"

# Zamaskuj PII
text = "Email: john@example.com, Phone: 555-123-4567"
redacted = redactor.redact(text)
print(redacted)  # "Email: [EMAIL_REDACTED], Phone: [PHONE_REDACTED]"

# Tokenizacja (odwracalna)
redactor_token = PIIRedactor(strategy="TOKENIZE")
tokenized, token_map = redactor_token.redact_with_tokens(text)
# Later: restore original
restored = redactor_token.restore(tokenized, token_map)
```

#### `PIIRouter`
Routing zapytań z PII:
```python
from security.pii_handler import PIIRouter

router = PIIRouter()

# Sprawdź czy backend może przetwarzać PII
should_block, reason = router.should_block(
    prompt="Email: john@example.com",
    backend_hint="cloud_llm"  # Cloud LLMs nie mogą
)

if should_block:
    print(f"Blocked: {reason}")
```

Reguły routingu:
```
Cloud LLMs (OpenAI, Anthropic, Google):
  - Mogą: PUBLIC, INTERNAL
  - NIE mogą: SENSITIVE, PII

On-prem LLMs (Ollama, LM Studio):
  - Mogą: PUBLIC, INTERNAL, SENSITIVE, PII
```

### 3. Audit Logging (`audit.py`)

#### `AuditLogger`
Logowanie zdarzeń audit:
```python
from security.audit import AuditLogger, Outcome

logger = AuditLogger(log_file="audit.log")

# Log authorization
logger.log_authorization(
    request_id="req-123",
    client_id="app-456",
    action="process",
    is_authorized=True
)

# Log PII detection
logger.log_pii_detection(
    request_id="req-123",
    pii_types=["email", "phone"],
    action_taken="routed_to_private_backend"
)

# Log processing
logger.log_processing(
    request_id="req-123",
    backend="openai:gpt-3.5",
    outcome=Outcome.SUCCESS,
    latency_ms=450,
    cost_usd=0.0001
)

# Log security violation
logger.log_security_violation(
    request_id="req-123",
    violation_type="pii_in_cloud_backend",
    details={'backend': 'openai', 'pii_types': ['email']}
)
```

## 🚀 Instalacja

```bash
cd components/security
pip install -r requirements.txt
```

## 📊 Audit Log Format

```json
{
  "timestamp": "2025-01-15T10:30:00.123Z",
  "request_id": "req-abc123",
  "event_type": "authorization",
  "client_id": "app-456",
  "action": "process",
  "is_authorized": true,
  "reason": null,
  "metadata": {}
}
```

## 🔒 Security Best Practices

### 1. JWT Secrets
```python
# ❌ NIE rób tego:
jwt_secret = "my-secret"

# ✅ Zrób to:
import os
jwt_secret = os.getenv("JWT_SECRET")  # Z KMS lub Vault
```

### 2. PII Handling
```python
# Zawsze wykrywaj PII przed wysłaniem do cloud LLM
if detector.detect(prompt).has_pii:
    # Route do on-prem LLM
    backend = "local:ollama"
else:
    # Możesz użyć cloud LLM
    backend = "openai:gpt-3.5"
```

### 3. Audit Everything
```python
# Loguj wszystkie krytyczne operacje
audit.log_authorization(...)
audit.log_pii_detection(...)
audit.log_processing(...)
audit.log_security_violation(...)
```

## 🔗 Zależności

### Używane przez
- Collection Layer - wszystkie security features

### Współdzielone
- Shared schemas - dla kontraktów

## 📖 Więcej Informacji

- [Collection Layer](../collection-layer/README.md) - Używa security components
- [Główny README](../../README.md) - Przegląd systemu
