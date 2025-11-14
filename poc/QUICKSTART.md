# Quick Start - 5 minut do działającego systemu

## Krok 1: Instalacja (1 minuta)

```bash
cd poc
pip install -r requirements.txt
```

## Krok 2: Konfiguracja (1 minuta)

```bash
# Skopiuj przykładową konfigurację
cp .env.example .env

# Edytuj i dodaj swój klucz API
nano .env
```

W pliku `.env`:
```bash
OPENAI_API_KEY=sk-twoj-klucz-tutaj
```

## Krok 3: Uruchom prosty przykład (1 minuta)

```bash
python simple_example.py
```

Zobaczysz:
```
🤖 Simple AI Monitoring Example

Making API calls...

📝 Event: gpt-3.5-turbo - 28 tokens - $0.0001
Response: 2 + 2 equals 4.

📝 Event: gpt-3.5-turbo - 35 tokens - $0.0002
🚨 HIGH: Personally Identifiable Information (PII) detected
Response: I'll help you with that...

📝 Event: gpt-3.5-turbo - 42 tokens - $0.0002
🚨 CRITICAL: Potential prompt injection attack detected
Response: I cannot ignore my instructions...

==================================================
📊 Summary:
  Total requests: 3
  Total cost: $0.0005
  PII detected: 1
  Injections: 1
  Anomalies: 2

💾 Data saved to: simple_demo.db
```

## Krok 4: Zobacz szczegóły w CLI (2 minuty)

```bash
python cli.py
```

Menu interaktywne:
```
Choose an option:

1. View Statistics
2. View Recent Events
3. View Recent Anomalies
4. View High Risk Events
5. Exit

Enter choice (1-5):
```

Lub bezpośrednio:
```bash
python cli.py stats           # Statystyki
python cli.py events          # Wydarzenia
python cli.py anomalies       # Anomalie
python cli.py risks           # Wysokie ryzyko
```

## Gotowe! 🎉

Teraz każde wywołanie API jest:
- ✅ Automatycznie monitorowane
- ✅ Analizowane pod kątem bezpieczeństwa
- ✅ Sprawdzane pod kątem kosztów
- ✅ Zapisywane do bazy danych

## Użycie we własnym kodzie

```python
from openai import OpenAI
from collector import OpenAICollector
from processor import EventProcessor
from storage import EventStorage
from analyzer import AnomalyDetector

# Setup (raz)
storage = EventStorage()
processor = EventProcessor()
analyzer = AnomalyDetector()

async def handle_event(event):
    event = processor.process_event(event)
    storage.store_event(event)

    anomalies = analyzer.analyze_event(event, [])
    for anomaly in anomalies:
        print(f"Alert: {anomaly.description}")

# Użyj
client = OpenAI()
monitored = OpenAICollector(client, event_handler=handle_event)

# Normalne wywołania - automatycznie monitorowane!
response = monitored.client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## Troubleshooting

**Problem**: `ImportError: No module named 'openai'`
```bash
pip install openai anthropic
```

**Problem**: `No API key found`
```bash
export OPENAI_API_KEY=sk-your-key
# lub edytuj .env
```

**Problem**: `Database is locked`
```bash
# Zamknij wszystkie połączenia, usuń .db-wal i .db-shm
rm *.db-wal *.db-shm
```

## Następne kroki

- Przeczytaj pełny [README.md](README.md) dla zaawansowanych opcji
- Zobacz [main.py](main.py) dla kompletnego przykładu
- Dostosuj thresholdy w `AnomalyDetector` config
- Dodaj własne wzorce wykrywania
