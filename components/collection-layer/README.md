# Collection Layer - MPC Server

**Warstwa Zbierania** - Centralny gateway do routowania zapytań AI.

## 📋 Opis

MPC (Multi-Provider Coordinator) Server to serce systemu AI SIEM. Odbiera zapytania od aplikacji (Application Layer) i inteligentnie kieruje je do odpowiednich backendów (Processing Layer).

## 🎯 Funkcje

### 1. Request Validation
- Walidacja schematów JSON-RPC
- Sprawdzanie poprawności payload

### 2. Authentication & Authorization
- JWT token validation
- Role-based access control (RBAC)
- Permission checking

### 3. PII Detection & Routing
- Automatyczne wykrywanie PII (email, telefon, SSN, karty kredytowe)
- Routing do backendów obsługujących PII
- Blokowanie zapytań z PII do niewłaściwych backendów

### 4. Intelligent Routing
- **Capability-based**: Wybór backendu po wymaganych capability
- **Cost-aware**: Optymalizacja kosztów
- **Latency-aware**: Minimalizacja opóźnień
- **Cascade routing**: Fallback przy niskiej pewności

### 5. Audit Logging
- Pełny audit trail wszystkich zapytań
- Security violation tracking
- Performance metrics

## 🚀 Instalacja

```bash
cd components/collection-layer
pip install -r requirements.txt
```

## 💡 Użycie

### Uruchomienie Serwera

```python
from server import MPCServer

# Utwórz serwer
server = MPCServer(
    jwt_secret="your-jwt-secret",
    hmac_secret="your-hmac-secret",
    enable_pii_detection=True,
    enable_audit=True
)

# Przetwórz zapytanie
response = await server.process_request(request)
```

### Health Check

```python
health = server.health_check()
print(health)
# {
#   'status': 'healthy',
#   'components': {
#     'router': 'ok',
#     'pii_detector': 'ok',
#     'audit': 'ok'
#   }
# }
```

## 🛣️ Routing Pipeline

```
1. Validate Request Schema
   ↓
2. Authenticate (JWT)
   ↓
3. Authorize (RBAC)
   ↓
4. Detect PII
   ↓
5. PII-aware Routing Check
   ↓
6. Infer Capability
   ↓
7. Select Backend (IntelligentRouter)
   ↓
8. Forward to Processing Layer
   ↓
9. Return Response + Audit Log
```

## 🧠 Intelligent Router

### Routing Strategies

```python
from router import IntelligentRouter, CapabilityType
from shared.schemas.contracts import SensitivityLevel, ProcessingHint

router = IntelligentRouter(backends)

# Strategy 1: Capability-based
decision = router.route(
    capability=CapabilityType.SECURITY_SCAN,
    sensitivity=SensitivityLevel.INTERNAL
)

# Strategy 2: Cost-optimized
decision = router.route(
    capability=CapabilityType.TEXT_GENERATION,
    max_cost=0.01,
    processing_hint=ProcessingHint.RULE_ENGINE
)

# Strategy 3: Cascade with fallbacks
decision = router.route(
    capability=CapabilityType.CLASSIFICATION,
    use_cascade=True,
    fallback_backends=["rules:classifier", "model:small:classifier"]
)
```

### Backend Selection Criteria

| Kryteria | Waga | Opis |
|----------|------|------|
| Capability Match | 40% | Czy backend obsługuje wymagane capability |
| Sensitivity Support | 30% | Czy backend może przetwarzać dane o danej wrażliwości |
| Cost | 15% | Koszt przetworzenia |
| Latency | 10% | Oczekiwane opóźnienie |
| Availability | 5% | Dostępność backendu |

## 🔒 Security Features

### PII Detection
```python
# Automatycznie wykrywane typy PII:
- EMAIL
- PHONE
- SSN (US Social Security Number)
- CREDIT_CARD
- IP_ADDRESS
- DATE_OF_BIRTH
```

### PII Routing Rules
```
IF PII detected AND backend != "pii-safe"
  → BLOCK request
  → Log security violation
ELSE
  → ALLOW request
```

### Authentication
```python
# JWT Token Required
{
  "client_id": "app-123",
  "role": "service",
  "permissions": ["READ", "EXECUTE"],
  "exp": 1234567890
}
```

## 📊 Audit Logs

Format logów:
```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "request_id": "req-abc123",
  "event_type": "processing",
  "client_id": "app-123",
  "backend": "rules:classifier",
  "outcome": "SUCCESS",
  "latency_ms": 45,
  "cost_usd": 0.0001
}
```

## 🔗 Zależności

### Wejście (od)
- Application Layer - zapytania od klientów

### Wyjście (do)
- Processing Layer - przekazywanie zapytań do backendów
- Storage Layer (opcjonalne) - audit logs

### Współdzielone
- Shared schemas - kontrakty JSON-RPC
- Security components - auth, PII detection

## 📖 Więcej Informacji

- [Application Layer](../application-layer/README.md) - Klient API
- [Processing Layer](../processing-layer/README.md) - Backendy przetwarzania
- [Security Components](../security/README.md) - Bezpieczeństwo
- [Główny README](../../README.md) - Przegląd systemu
