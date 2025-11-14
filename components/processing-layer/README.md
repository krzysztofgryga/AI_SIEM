# Processing Layer

**Warstwa Przetwarzania** - Backendy do przetwarzania zapytań AI.

## 📋 Opis

Processing Layer zawiera różne backendy, które rzeczywiście przetwarzają zapytania AI:
- **Rule Engines**: Szybkie, deterministyczne, bez kosztów
- **LLM Models**: OpenAI, Anthropic, Gemini, lokalne modele
- **Hybrid Systems**: Kombinacja reguł i LLM

## 🎯 Typy Backendów

### 1. Rule-Based Backends
```python
# Backend oparty o reguły
- Koszt: $0
- Latency: <10ms
- Use cases: Klasyfikacja, proste analizy
```

### 2. LLM Backends
```python
# Small Models (GPT-3.5, Claude Haiku)
- Koszt: $0.001 - $0.01
- Latency: 500-2000ms
- Use cases: Analiza logów, podsumowania

# Large Models (GPT-4, Claude Opus)
- Koszt: $0.01 - $0.10
- Latency: 1000-5000ms
- Use cases: Złożona analiza, reasoning
```

### 3. Hybrid Backends
```python
# Reguły + LLM fallback
- Koszt: $0 - $0.05 (zależy od przypadku)
- Latency: 10-2000ms (zależy od ścieżki)
- Use cases: Większość przypadków użycia
```

## 🚀 Instalacja

```bash
cd components/processing-layer
pip install -r requirements.txt
```

## 💡 Użycie

### Backend Registry

```python
from backends import (
    BackendRegistry,
    get_backend_registry,
    initialize_default_backends
)

# Inicjalizacja domyślnych backendów
initialize_default_backends()

# Pobierz registry
registry = get_backend_registry()

# Lista backendów
backends = registry.list_backends()
for backend_id in backends:
    backend = registry.get(backend_id)
    print(f"{backend_id}: {backend.capabilities}")
```

### Tworzenie Własnego Backendu

```python
from backends import ProcessingBackend, CapabilityType

class MyCustomBackend(ProcessingBackend):
    def __init__(self):
        super().__init__(
            backend_id="custom:my-backend",
            name="My Custom Backend",
            capabilities=[CapabilityType.TEXT_GENERATION],
            max_sensitivity=SensitivityLevel.INTERNAL,
            estimated_cost_per_1k_tokens=0.005,
            estimated_latency_ms=500
        )

    async def process(self, prompt: str, **kwargs):
        # Twoja logika przetwarzania
        result = my_processing_logic(prompt)

        return {
            "response": result,
            "tokens": 100,
            "cost": 0.001
        }

# Rejestracja
registry = get_backend_registry()
registry.register(MyCustomBackend())
```

## 📊 Dostępne Backendy

### Rule-Based

| Backend ID | Capability | Cost | Latency |
|-----------|------------|------|---------|
| `rules:classifier` | Classification | $0 | <10ms |
| `rules:extractor` | Extraction | $0 | <10ms |
| `rules:validator` | Validation | $0 | <10ms |

### LLM-Based

| Backend ID | Capability | Cost/1K | Latency |
|-----------|------------|---------|---------|
| `openai:gpt-3.5` | Text Gen | $0.001 | 500ms |
| `openai:gpt-4` | All | $0.030 | 2000ms |
| `anthropic:claude-haiku` | Text Gen | $0.001 | 600ms |
| `anthropic:claude-sonnet` | All | $0.015 | 1500ms |
| `google:gemini-pro` | Text Gen | $0.001 | 800ms |

### Local Models

| Backend ID | Capability | Cost | Latency |
|-----------|------------|------|---------|
| `local:ollama:llama2` | Text Gen | $0 | 1000ms |
| `local:lmstudio:mistral` | Text Gen | $0 | 800ms |

## 🎯 Capabilities

```python
class CapabilityType(str, Enum):
    TEXT_GENERATION = "text_generation"
    CLASSIFICATION = "classification"
    EXTRACTION = "extraction"
    SECURITY_SCAN = "security_scan"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
```

## 🔒 Sensitivity Support

Każdy backend deklaruje maksymalny poziom wrażliwości danych, które może przetwarzać:

```python
# Cloud LLMs
- PUBLIC, INTERNAL only
- NIE mogą przetwarzać PII

# On-prem LLMs
- PUBLIC, INTERNAL, SENSITIVE, PII
- Mogą przetwarzać wszystko
```

## 📈 Performance Metrics

Każdy backend raportuje:
```python
{
    "response": "...",
    "tokens": 150,
    "cost": 0.0023,
    "latency_ms": 450,
    "backend": "openai:gpt-3.5",
    "confidence": 0.95
}
```

## 🔗 Zależności

### Wejście (od)
- Collection Layer - zapytania od MPC Server

### Wyjście (do)
- External APIs (OpenAI, Anthropic, etc.) - dla cloud LLMs
- Local services (Ollama, LM Studio) - dla local LLMs

### Współdzielone
- Shared schemas - kontrakty

## 📖 Więcej Informacji

- [Collection Layer](../collection-layer/README.md) - MPC Server routing
- [Główny README](../../README.md) - Przegląd systemu
