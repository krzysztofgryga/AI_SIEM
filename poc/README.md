# AI Agent Monitoring - Proof of Concept

Minimalny system monitoringu agentów AI skupiony na 3 kluczowych krokach:
1. **Zbieranie** - przechwytywanie wywołań API
2. **Przetwarzanie** - normalizacja i wzbogacanie danych
3. **Analiza** - wykrywanie anomalii i zagrożeń

## 🎯 Funkcje

### Zbieranie Danych
- ✅ Automatyczne przechwytywanie wywołań OpenAI API
- ✅ Automatyczne przechwytywanie wywołań Anthropic API
- ✅ Pomiar latencji i kosztów
- ✅ Liczenie tokenów

### Przetwarzanie
- ✅ Normalizacja do wspólnego formatu
- ✅ Wykrywanie PII (email, telefon, SSN, karty kredytowe)
- ✅ Wykrywanie prób prompt injection
- ✅ Kalkulacja poziomu ryzyka

### Analiza
- ✅ Wykrywanie wysokich kosztów
- ✅ Wykrywanie wysokiej latencji
- ✅ Wykrywanie skoków kosztów/latencji
- ✅ Wykrywanie wysokiego error rate
- ✅ Analiza wzorców w czasie

### Storage & Reporting
- ✅ SQLite database dla prostoty
- ✅ CLI do przeglądania danych
- ✅ Statystyki w czasie rzeczywistym
- ✅ Alerty w konsoli

## 📦 Instalacja

```bash
# 1. Przejdź do katalogu POC
cd poc

# 2. Zainstaluj zależności
pip install -r requirements.txt

# 3. Skopiuj przykładową konfigurację
cp .env.example .env

# 4. Edytuj .env i dodaj swoje klucze API
nano .env
```

## 🚀 Użycie

### Przykład 1: Podstawowe użycie

```python
import asyncio
from openai import OpenAI
from collector import OpenAICollector
from processor import EventProcessor
from analyzer import AnomalyDetector
from storage import EventStorage

# Inicjalizacja
storage = EventStorage()
processor = EventProcessor()
analyzer = AnomalyDetector()

# Handler dla zdarzeń
async def handle_event(event):
    # Przetwórz
    event = processor.process_event(event)

    # Zapisz
    storage.store_event(event)

    # Analizuj
    anomalies = analyzer.analyze_event(event, [])
    for anomaly in anomalies:
        storage.store_anomaly(anomaly)
        print(f"🚨 {anomaly.description}")

# Użyj monitorowanego klienta
client = OpenAI()
monitored_client = OpenAICollector(
    client,
    event_handler=handle_event,
    user_id="user123"
)

# Normalne wywołania - automatycznie monitorowane!
response = monitored_client.client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Przykład 2: Uruchomienie demo

```bash
# Uruchom przykład z testowymi wywołaniami
python main.py
```

Wynik:
```
🤖 Starting OpenAI Monitoring Example

Making test API calls...

✓ Response: 2+2 equals 4.
✓ Response: You can contact support at...

🚨 ANOMALY DETECTED
Type: pii_detected
Severity: HIGH
Description: Personally Identifiable Information (PII) detected
Model: gpt-3.5-turbo
Action: Implement PII scrubbing and review data handling policies

📊 Monitoring Summary (Last 60 minutes)

┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Metric             ┃      Value ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ Total Requests     │          3 │
│ Successful         │          3 │
│ Failed             │          0 │
│ Success Rate       │      100%  │
│ Total Tokens       │      142   │
│ Avg Latency        │      850ms │
│ Total Cost         │   $0.0021  │
│ PII Detections     │          1 │
│ Injection Attempts │          1 │
└────────────────────┴────────────┘
```

### Przykład 3: Przeglądanie danych przez CLI

```bash
# Interaktywne menu
python cli.py

# Lub bezpośrednie komendy
python cli.py stats           # Statystyki
python cli.py events 20       # 20 ostatnich zdarzeń
python cli.py anomalies 10    # 10 ostatnich anomalii
python cli.py risks           # Zdarzenia wysokiego ryzyka
```

## 📊 Przykładowy Output CLI

```
╔════════════════════════════════════════╗
║   AI Monitoring Dashboard CLI          ║
╚════════════════════════════════════════╝

📊 Statistics (Last 24 Hours)

┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Metric           ┃    Value ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Total Events     │       47 │
│ Successful       │       45 │
│ Failed           │        2 │
│ Success Rate     │    95.7% │
│ Total Tokens     │    8,234 │
│ Total Cost       │ $0.0421  │
│ Avg Latency      │    723ms │
│ PII Events       │        3 │
│ Injection        │        1 │
│ Anomalies        │        7 │
└──────────────────┴──────────┘

📝 Recent Events (Last 10)

┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━┳━━━━━━━━┓
┃ Time             ┃ Provider┃ Model       ┃Tokens┃ Cost   ┃Latency┃Status┃ Risk   ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━━╇━━━━━━━━┩
│ 2025-01-15 14:23 │ openai  │ gpt-4       │  342 │$0.0142 │  892ms│  ✓   │ medium │
│ 2025-01-15 14:22 │ anthropic│ claude-3... │  128 │$0.0008 │  654ms│  ✓   │ low    │
└──────────────────┴─────────┴─────────────┴──────┴────────┴───────┴──────┴────────┘
```

## 🔍 Wykrywane Anomalie

| Typ Anomalii | Opis | Severity |
|-------------|------|----------|
| `high_cost` | Pojedyncze żądanie > $0.50 | HIGH |
| `cost_spike` | Koszt 3x wyższy niż średnia | HIGH |
| `high_latency` | Latencja > 5000ms | MEDIUM |
| `latency_spike` | Latencja 3x wyższa niż średnia | MEDIUM |
| `high_token_usage` | Tokeny > 8000 | MEDIUM |
| `request_failure` | Błąd API | HIGH |
| `prompt_injection` | Wykryto próbę injection | CRITICAL |
| `pii_detected` | Wykryto dane osobowe | HIGH |
| `high_error_rate` | Error rate > 10% | CRITICAL |
| `model_errors` | Wysokie błędy dla modelu | HIGH |
| `high_request_rate` | > 50 req/min | MEDIUM |
| `high_cost_rate` | > $10/godzinę | HIGH |

## 📁 Struktura Projektu

```
poc/
├── models.py           # Modele danych (Pydantic)
├── collector.py        # Interceptory dla OpenAI/Anthropic
├── processor.py        # Przetwarzanie i normalizacja
├── analyzer.py         # Wykrywanie anomalii
├── storage.py          # SQLite storage
├── main.py            # Główny przykład użycia
├── cli.py             # CLI do przeglądania danych
├── requirements.txt   # Zależności
├── .env.example       # Przykładowa konfiguracja
└── README.md          # Ta dokumentacja
```

## 🎓 Najważniejsze Klasy

### `OpenAICollector` / `AnthropicCollector`
Wrapper dla API klientów - automatycznie przechwytuje wywołania.

### `EventProcessor`
Przetwarza zdarzenia:
- Wykrywa PII
- Wykrywa prompt injection
- Kalkuluje poziom ryzyka

### `EventAggregator`
Agreguje metryki w czasie.

### `AnomalyDetector`
Wykrywa anomalie:
- Na poziomie pojedynczego zdarzenia
- Na poziomie wzorców (wiele zdarzeń)

### `EventStorage`
Prosty SQLite storage z indeksami.

## ⚙️ Konfiguracja

Konfiguracja anomaly detectora (w kodzie):

```python
detector = AnomalyDetector(config={
    'cost_threshold_usd': 0.5,      # Alert przy koszcie > $0.50
    'latency_threshold_ms': 5000,    # Alert przy latencji > 5s
    'error_rate_threshold': 0.1,     # Alert przy błędach > 10%
    'token_threshold': 8000,         # Alert przy tokenach > 8000
    'spike_multiplier': 3.0          # Alert gdy 3x wyższe niż średnia
})
```

## 🔐 Bezpieczeństwo

POC wykrywa:
- **PII**: email, telefon, SSN, karty kredytowe, adresy IP
- **Prompt Injection**: znane wzorce ataków
- **Anomalie kosztów**: nietypowe wykorzystanie
- **Błędy**: monitoring niepowodzeń

**Uwaga**: To POC. W produkcji dodaj:
- Szyfrowanie danych w bazie
- Uwierzytelnianie/autoryzację
- Rate limiting
- Rotację logów
- Secure secrets management

## 📈 Roadmap (Przyszłe Rozszerzenia)

Jeśli POC się sprawdzi, można dodać:

1. **Storage**:
   - Elasticsearch dla skalowalności
   - InfluxDB dla metryk czasowych
   - S3 dla archiwizacji

2. **Processing**:
   - Kafka dla streamingu
   - Apache Beam dla złożonego przetwarzania
   - ML models dla lepszej detekcji anomalii

3. **Analytics**:
   - Predictive models
   - Behavioral analysis
   - Cost forecasting

4. **Alerting**:
   - Slack integration
   - PagerDuty integration
   - Email notifications
   - Webhooks

5. **Dashboards**:
   - Grafana dashboards
   - Streamlit web UI
   - Real-time updates

6. **Compliance**:
   - GDPR compliance checks
   - Audit trails
   - Data retention policies

## 🤝 Contributing

To jest POC - fork, modify, improve!

## 📄 License

MIT License - use freely!

## ❓ FAQ

**Q: Czy to spowalnia wywołania API?**
A: Overhead <10ms - większość to czas zapisu do SQLite.

**Q: Czy działa z async/await?**
A: Tak, event handler może być async.

**Q: Czy mogę monitorować wiele klientów jednocześnie?**
A: Tak, po prostu stwórz wiele collectorów z tym samym handlerem.

**Q: Jak długo przechowywane są dane?**
A: Domyślnie nieskończenie w SQLite. Użyj `aggregator.clear_old_events(days=7)`.

**Q: Czy mogę użyć z innymi providerami (Cohere, etc.)?**
A: Tak - stwórz własny Collector wzorowany na OpenAICollector.

## 📞 Support

Pytania? Issues? PRs welcome!
