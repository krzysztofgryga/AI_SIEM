# Application Layer

**Warstwa Aplikacji** - Interfejs klienta dla aplikacji korzystających z AI SIEM.

## 📋 Opis

Warstwa aplikacji dostarcza klientom prosty interfejs do komunikacji z systemem AI SIEM. Wszystkie zapytania przechodzą przez centralny MPC Server (Collection Layer), eliminując bezpośredni dostęp do modeli AI.

## 🎯 Główne Komponenty

### `MPCClient`
Pełny klient z kontrolą nad wszystkimi parametrami:
- Konfiguracja sensitivity levels
- Processing hints (reguły vs LLM)
- PII detection
- Timeouts i retries

### `SimpleMPCClient`
Uproszczony klient z domyślnymi ustawieniami:
- Prosta metoda `ask()`
- Automatyczna konfiguracja
- Idealne dla szybkiego prototypowania

## 🚀 Instalacja

```bash
cd components/application-layer
pip install -r requirements.txt
```

## 💡 Przykłady Użycia

### Przykład 1: Prosty Klient

```python
import asyncio
from client import SimpleMPCClient

async def main():
    # Utwórz klienta
    client = SimpleMPCClient(auth_token="demo-token")

    # Zadaj pytanie
    response = await client.ask("What is API security?")
    print(response)

asyncio.run(main())
```

### Przykład 2: Zaawansowana Konfiguracja

```python
from client import MPCClient
from shared.schemas.contracts import SensitivityLevel, ProcessingHint

async def main():
    # Klient z pełną konfiguracją
    client = MPCClient(
        application_id="my-app",
        auth_token="your-token",
        environment="production"
    )

    # Wyślij zapytanie z ustawieniami bezpieczeństwa
    result = await client.process(
        prompt="Analyze this security log",
        sensitivity=SensitivityLevel.SENSITIVE,
        processing_hint=ProcessingHint.MODEL_PRIVATE,
        enable_pii_detection=True
    )

    print(result['response'])

asyncio.run(main())
```

### Przykład 3: Batch Processing

```python
async def main():
    client = SimpleMPCClient()

    # Przetwórz wiele zapytań
    questions = [
        "What is a SQL injection?",
        "Explain XSS attacks",
        "What is CSRF?"
    ]

    results = await client.batch_process(questions)

    for q, r in zip(questions, results):
        print(f"Q: {q}\nA: {r['response']}\n")

asyncio.run(main())
```

## 🔒 Sensitivity Levels

| Level | Użycie | Backend |
|-------|--------|---------|
| `PUBLIC` | Dane publiczne | Wszystkie backendy |
| `INTERNAL` | Dane wewnętrzne | Zaufane backendy |
| `SENSITIVE` | Dane wrażliwe | Prywatne backendy |
| `PII` | Dane osobowe | Tylko on-prem |

## ⚙️ Processing Hints

| Hint | Strategia | Koszt |
|------|-----------|-------|
| `AUTO` | Automatyczny wybór | Zależy |
| `RULE_ENGINE` | Tylko reguły | $0 |
| `MODEL_SMALL` | Mały model | $ |
| `MODEL_LARGE` | Duży model | $$$ |
| `HYBRID` | Reguły → LLM fallback | $-$$ |

## 📊 Health Check

```python
async def check_health():
    client = MPCClient()
    health = await client.health_check()
    print(health)
```

## 🔗 Zależności

- Collection Layer (MPC Server) musi być uruchomiony
- Shared schemas dla kontraktów

## 📖 Więcej Informacji

- [Collection Layer](../collection-layer/README.md) - MPC Server
- [Przykłady](../../examples/README.md) - Więcej przykładów użycia
- [Główny README](../../README.md) - Przegląd systemu
