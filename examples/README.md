# Examples - Przykłady Użycia

Przykłady pokazujące różne sposoby użycia AI SIEM.

## 📋 Dostępne Przykłady

### 1. `basic_usage.py` - Podstawowe Użycie
Najprostszy przykład - jak wysłać zapytanie i otrzymać odpowiedź.

```bash
python examples/basic_usage.py
```

**Pokazuje:**
- Tworzenie SimpleMPCClient
- Wysyłanie prostych zapytań
- Używanie flag bezpieczeństwa

### 2. `secure_usage.py` - Użycie z Danymi Wrażliwymi
Przykład pokazujący jak obsługiwać różne poziomy wrażliwości danych.

```bash
python examples/secure_usage.py
```

**Pokazuje:**
- Sensitivity levels (PUBLIC, INTERNAL, SENSITIVE, PII)
- Processing hints (AUTO, RULE_ENGINE, MODEL_PRIVATE)
- PII detection i routing
- Security flags

### 3. `batch_processing.py` - Przetwarzanie Wsadowe
Przetwarzanie wielu zapytań jednocześnie z metrykami.

```bash
python examples/batch_processing.py
```

**Pokazuje:**
- Batch processing
- Obliczanie metryk (czas, koszt)
- Optymalizacja backendów

## 🚀 Wymagania

```bash
# Zainstaluj zależności dla wszystkich komponentów
pip install -r components/application-layer/requirements.txt
pip install -r components/collection-layer/requirements.txt
pip install -r components/processing-layer/requirements.txt
```

## 💡 Jak Uruchomić

### Opcja 1: Bezpośrednio
```bash
python examples/basic_usage.py
```

### Opcja 2: Jako moduł
```bash
python -m examples.basic_usage
```

## 📊 Oczekiwany Output

### basic_usage.py
```
============================================================
AI SIEM - Basic Usage Example
============================================================

📋 Creating SimpleMPCClient...
✓ Client created

📝 Sending simple query...
   Q: What is API security?
   A: Processed by rules:classifier: What is API security?...

🔒 Sending secure query (uses private model)...
   Q: Explain XSS attacks
   A: Processed by model:private: Explain XSS attacks...

============================================================
✓ Example completed!
============================================================
```

## 🔧 Dostosowywanie Przykładów

### Zmiana Auth Token
```python
client = SimpleMPCClient(
    auth_token="your-custom-token",  # Zmień tutaj
    application_id="your-app"
)
```

### Zmiana Processing Hint
```python
result = await client.process(
    prompt="Your question",
    processing_hint=ProcessingHint.MODEL_LARGE,  # Użyj dużego modelu
    sensitivity=SensitivityLevel.INTERNAL
)
```

### Dodanie Własnych Zapytań
```python
questions = [
    "Your question 1",
    "Your question 2",
    # ...
]
results = await client.client.batch_process(questions)
```

## 🐛 Troubleshooting

### Problem: ModuleNotFoundError
```bash
# Upewnij się, że jesteś w głównym katalogu
cd /path/to/AI_SIEM
python examples/basic_usage.py
```

### Problem: Authentication Failed
```bash
# Sprawdź czy Collection Layer jest uruchomiony
# lub użyj domyślnego tokena "demo-token"
```

### Problem: Import Error
```bash
# Dodaj ścieżkę do PYTHONPATH
export PYTHONPATH=/path/to/AI_SIEM:$PYTHONPATH
python examples/basic_usage.py
```

## 📖 Więcej Informacji

- [Application Layer](../components/application-layer/README.md) - Client API
- [Collection Layer](../components/collection-layer/README.md) - MPC Server
- [Główny README](../README.md) - Przegląd systemu
