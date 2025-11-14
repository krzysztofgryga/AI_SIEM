# Storage Layer

**Warstwa Przechowywania** - Perzystencja danych i analiza anomalii.

## 📋 Opis

Storage Layer odpowiada za:
- Przechowywanie eventów AI (zapytania, odpowiedzi, metryki)
- Wykrywanie anomalii (koszty, latencja, bezpieczeństwo)
- Agregację metryk
- Generowanie raportów

## 🎯 Komponenty

### `EventStorage`
Główny komponent do przechowywania danych:
- SQLite database
- Indeksowane zapytania
- CRUD operations dla eventów i anomalii

### `AnomalyDetector`
Wykrywanie anomalii:
- Threshold-based detection
- Spike detection (3x średnia)
- Pattern analysis
- Security violation detection

## 🚀 Instalacja

```bash
cd components/storage-layer
pip install -r requirements.txt
```

## 💡 Użycie

### Event Storage

```python
from storage import EventStorage
from shared.models import AIEvent, EventType, Provider

# Inicjalizacja
storage = EventStorage(db_path="ai_monitoring.db")

# Zapisz event
event = AIEvent(
    event_type=EventType.RESPONSE,
    provider=Provider.OPENAI,
    model="gpt-3.5-turbo",
    prompt="Hello",
    response="Hi there!",
    latency_ms=450,
    cost_usd=0.0001,
    success=True
)
storage.store_event(event)

# Pobierz ostatnie eventy
recent = storage.get_recent_events(limit=10)

# Statystyki
stats = storage.get_statistics(hours=24)
print(f"Total requests: {stats['total_requests']}")
print(f"Success rate: {stats['success_rate']:.1%}")
print(f"Total cost: ${stats['total_cost_usd']:.4f}")
```

### Anomaly Detection

```python
from analyzer import AnomalyDetector

# Inicjalizacja z konfiguracją
detector = AnomalyDetector(config={
    'cost_threshold_usd': 0.5,       # Alert gdy koszt > $0.50
    'latency_threshold_ms': 5000,    # Alert gdy latencja > 5s
    'error_rate_threshold': 0.1,     # Alert gdy błędy > 10%
    'token_threshold': 8000,         # Alert gdy tokeny > 8000
    'spike_multiplier': 3.0          # Alert gdy 3x wyższe niż średnia
})

# Analiza pojedynczego eventu
anomalies = detector.analyze_event(event, recent_events)

for anomaly in anomalies:
    print(f"⚠️ {anomaly.anomaly_type}: {anomaly.description}")
    if anomaly.severity in ['critical', 'high']:
        print(f"🚨 Action: {anomaly.recommended_action}")

# Analiza wzorców
pattern_anomalies = detector.analyze_patterns(
    events=storage.get_recent_events(100),
    window_minutes=60
)
```

## 📊 Wykrywane Anomalie

### Event-Level Anomalies

| Typ | Threshold | Severity | Opis |
|-----|-----------|----------|------|
| `high_cost` | > $0.50 | HIGH | Pojedyncze zapytanie jest kosztowne |
| `high_latency` | > 5000ms | MEDIUM | Długi czas odpowiedzi |
| `high_token_usage` | > 8000 | MEDIUM | Dużo tokenów w zapytaniu |
| `request_failure` | - | HIGH | Błąd API |
| `prompt_injection` | - | CRITICAL | Wykryto próbę injection |
| `pii_detected` | - | HIGH | Dane osobowe w promptcie |

### Pattern-Level Anomalies

| Typ | Threshold | Severity | Opis |
|-----|-----------|----------|------|
| `cost_spike` | 3x avg | HIGH | Nagły wzrost kosztów |
| `latency_spike` | 3x avg | MEDIUM | Nagły wzrost latencji |
| `high_error_rate` | > 10% | CRITICAL | Wysoki wskaźnik błędów |
| `model_errors` | > 5 w 10min | HIGH | Problemy z konkretnym modelem |
| `high_request_rate` | > 50/min | MEDIUM | Nietypowa liczba zapytań |
| `high_cost_rate` | > $10/h | HIGH | Wysokie koszty w czasie |

## 🗄️ Schema Bazy Danych

### Tabela `events`
```sql
CREATE TABLE events (
    id TEXT PRIMARY KEY,
    timestamp TEXT,
    event_type TEXT,
    provider TEXT,
    model TEXT,
    prompt TEXT,
    response TEXT,
    latency_ms REAL,
    tokens_prompt INTEGER,
    tokens_completion INTEGER,
    tokens_total INTEGER,
    cost_usd REAL,
    success BOOLEAN,
    error_message TEXT,
    risk_level TEXT,
    has_pii BOOLEAN,
    has_injection BOOLEAN,
    user_id TEXT,
    session_id TEXT
)
```

### Tabela `anomalies`
```sql
CREATE TABLE anomalies (
    id TEXT PRIMARY KEY,
    timestamp TEXT,
    event_id TEXT,
    anomaly_type TEXT,
    severity TEXT,
    description TEXT,
    recommended_action TEXT,
    metadata TEXT
)
```

## 📈 Przykładowe Zapytania

### Top Costly Requests
```python
events = storage.get_events_by_cost(
    min_cost=0.01,
    limit=10
)
```

### Events with PII
```python
pii_events = storage.get_events_with_pii(
    hours=24
)
```

### High Risk Events
```python
risky = storage.get_high_risk_events(
    hours=24,
    min_risk_level="high"
)
```

## 🔒 Data Retention

```python
from storage import EventStorage

storage = EventStorage()

# Usuń stare eventy (starsze niż 30 dni)
deleted_count = storage.cleanup_old_events(days=30)

# Archiwizuj do JSON
storage.archive_events(
    output_file="archive_2025_01.json",
    start_date="2025-01-01",
    end_date="2025-01-31"
)
```

## 🔗 Zależności

### Wejście (od)
- Collection Layer - eventy do zapisania
- Processing Layer (opcjonalne) - metryki przetwarzania

### Wyjście (do)
- Tools (CLI) - dane do wyświetlenia
- Dashboards (przyszłość) - metryki i wykresy

### Współdzielone
- Shared models - AIEvent, Anomaly

## 📖 Więcej Informacji

- [Tools (CLI)](../../tools/README.md) - Narzędzia CLI do przeglądania danych
- [Główny README](../../README.md) - Przegląd systemu
