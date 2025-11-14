# 🚀 Quick Start - Nowa Architektura 3-Warstwowa

## Szybki Start (5 minut)

### 1. Instalacja Zależności

```bash
cd AI_SIEM/poc
pip install pydantic pyjwt httpx
```

### 2. Pierwszy Przykład

```python
import asyncio
from application.client import SimpleMPCClient

async def main():
    # Utwórz klienta
    client = SimpleMPCClient(auth_token="demo-token")

    # Zadaj pytanie
    response = await client.ask("What is API security?")
    print(response)

asyncio.run(main())
```

### 3. Uruchom Pełne Przykłady

```bash
python -m application.example_usage
```

## Struktura Projektu

```
poc/
├── schemas/              # 📋 Kontrakty JSON-RPC
│   ├── contracts.py      # MPCRequest, MPCResponse, etc.
│   └── __init__.py
│
├── security/             # 🔒 Bezpieczeństwo
│   ├── pii_handler.py    # PII detection/redaction/routing
│   ├── auth.py           # Authentication & authorization
│   ├── audit.py          # Audit logging
│   └── __init__.py
│
├── mpc_server/           # 🔄 Collection Layer
│   ├── server.py         # Główny MPC Server
│   ├── router.py         # Intelligent routing
│   └── __init__.py
│
├── processing/           # ⚙️ Processing Layer
│   ├── backends.py       # Processing backends
│   └── __init__.py
│
└── application/          # 🎯 Application Layer
    ├── client.py         # MPC Client
    ├── example_usage.py  # Przykłady
    └── __init__.py
```

## Podstawowe Użycie

### Application Layer (Klient)

```python
from application.client import MPCClient
from schemas.contracts import SensitivityLevel, ProcessingHint

# Utwórz klienta
client = MPCClient(
    application_id="my-app",
    auth_token="your-token"
)

# Wyślij zapytanie
result = await client.process(
    prompt="Analyze this log",
    sensitivity=SensitivityLevel.INTERNAL,
    processing_hint=ProcessingHint.AUTO
)

print(result['response'])
```

### Collection Layer (MPC Server)

```python
from mpc_server.server import MPCServer
from schemas.contracts import MPCRequest

# Utwórz serwer
server = MPCServer(
    jwt_secret="your-secret",
    enable_pii_detection=True,
    enable_audit=True
)

# Przetwórz zapytanie
response = await server.process_request(request)
```

### Processing Layer (Backendy)

```python
from processing.backends import (
    get_backend_registry,
    initialize_default_backends
)

# Inicjalizacja
initialize_default_backends()

# Użycie
registry = get_backend_registry()
backend = registry.get("rules:classifier")

result = await backend.process("Classify: ERROR message")
```

## Kluczowe Koncepcje

### 1. Sensitivity Levels

| Level | Użycie | Backend |
|-------|--------|---------|
| `PUBLIC` | Dane publiczne | Wszystkie |
| `INTERNAL` | Dane wewnętrzne | Zaufane |
| `SENSITIVE` | Dane wrażliwe | Prywatne |
| `PII` | Dane osobowe | On-prem only |

### 2. Processing Hints

| Hint | Strategia | Koszt |
|------|-----------|-------|
| `AUTO` | Automatyczny wybór | Zależy |
| `RULE_ENGINE` | Tylko reguły | $0 |
| `MODEL_SMALL` | Mały model | $ |
| `MODEL_LARGE` | Duży model | $$$ |
| `HYBRID` | Reguły → LLM | $-$$ |

### 3. Routing Strategies

```python
# Capability routing - wybór po capabilities
capability=CapabilityType.SECURITY_SCAN

# Cost-aware - optymalizacja kosztów
max_cost=0.1, max_latency_ms=5000

# Cascade - fallback jeśli niska pewność
use_cascade=True, fallback_backends=[...]

# PII-aware - routing po wykryciu PII
sensitivity=SensitivityLevel.PII → private model
```

## Przykłady

### Przykład 1: Basic

```python
client = SimpleMPCClient()
response = await client.ask("Hello, how are you?")
```

### Przykład 2: PII

```python
response = await client.ask_secure(
    "My email is user@example.com",
    contains_pii=True
)
```

### Przykład 3: Cost Optimization

```python
# Cheap
result = await client.process(
    prompt="Classify: ERROR",
    processing_hint=ProcessingHint.RULE_ENGINE
)
# Cost: $0.0000

# Expensive
result = await client.process(
    prompt="Analyze architecture",
    processing_hint=ProcessingHint.MODEL_LARGE
)
# Cost: $0.0234
```

### Przykład 4: Batch

```python
results = await client.batch_process([
    "Question 1",
    "Question 2",
    "Question 3"
])
```

## Więcej Informacji

- **[ARCHITECTURE.md](../ARCHITECTURE.md)** - Pełna dokumentacja architektury
- **[FLOW_DIAGRAM.md](../FLOW_DIAGRAM.md)** - Diagram przepływu
- **[README.md](../README.md)** - Przegląd projektu
- **[example_usage.py](application/example_usage.py)** - Wszystkie przykłady

## Troubleshooting

### Problem: ModuleNotFoundError

```bash
# Upewnij się, że jesteś w katalogu poc/
cd AI_SIEM/poc

# Zainstaluj zależności
pip install pydantic pyjwt httpx
```

### Problem: Import Error

```python
# Uruchamiaj przez moduł
python -m application.example_usage

# NIE: python application/example_usage.py
```

### Problem: JWT Error

```python
# Utwórz poprawny token
from security.auth import AccessControl, Role, Permission

ac = AccessControl("secret", "secret")
token = ac.create_service_token(
    "my-service",
    [Permission.READ, Permission.EXECUTE]
)

client = MPCClient(auth_token=token)
```

## Next Steps

1. ✅ Przeczytaj [ARCHITECTURE.md](../ARCHITECTURE.md)
2. ✅ Uruchom `python -m application.example_usage`
3. ✅ Spróbuj własnych przykładów
4. ✅ Zintegruj z własną aplikacją
