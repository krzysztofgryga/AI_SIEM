# Tools - CLI & Utilities

**Narzędzia** - CLI do zarządzania i monitorowania systemu AI SIEM.

## 📋 Opis

Tools zawiera narzędzia wiersza poleceń do:
- Przeglądania eventów i anomalii
- Generowania statystyk i raportów
- Monitorowania systemu w czasie rzeczywistym
- Exportu danych

## 🎯 Główne Narzędzie

### CLI Dashboard (`cli.py`)
Interaktywny dashboard do przeglądania danych.

## 🚀 Instalacja

```bash
cd tools
pip install -r requirements.txt
```

## 💡 Użycie

### Interaktywne Menu
```bash
python cli.py
```

Wyświetli menu:
```
╔════════════════════════════════════════╗
║   AI Monitoring Dashboard CLI          ║
╚════════════════════════════════════════╝

1. Statistics (24h)
2. Recent Events (20)
3. Recent Anomalies (10)
4. High Risk Events
5. PII Events
6. Cost Report
7. Exit

Select option:
```

### Bezpośrednie Komendy

```bash
# Statystyki (ostatnie 24h)
python cli.py stats

# 20 ostatnich eventów
python cli.py events 20

# 10 ostatnich anomalii
python cli.py anomalies 10

# Eventy wysokiego ryzyka
python cli.py risks

# Eventy z PII
python cli.py pii

# Raport kosztów
python cli.py costs

# Eventy dla konkretnego modelu
python cli.py model gpt-4

# Eventy dla konkretnego providera
python cli.py provider openai
```

## 📊 Przykładowy Output

### Statistics
```
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

By Provider:
  • openai: 32 requests
  • anthropic: 15 requests

By Model:
  • gpt-3.5-turbo: 25 requests
  • claude-3-haiku: 15 requests
  • gpt-4: 7 requests
```

### Recent Events
```
📝 Recent Events (Last 10)

┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━┳━━━━━━━━┓
┃ Time             ┃ Provider┃ Model       ┃Tokens┃ Cost   ┃Latency┃Status┃ Risk   ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━━╇━━━━━━━━┩
│ 2025-01-15 14:23 │ openai  │ gpt-4       │  342 │$0.0142 │  892ms│  ✓   │ medium │
│ 2025-01-15 14:22 │ anthropic│ claude-3... │  128 │$0.0008 │  654ms│  ✓   │ low    │
│ 2025-01-15 14:21 │ openai  │ gpt-3.5-... │   89 │$0.0001 │  423ms│  ✓   │ low    │
│ 2025-01-15 14:20 │ openai  │ gpt-4       │  456 │$0.0189 │ 1205ms│  ✗   │ high   │
└──────────────────┴─────────┴─────────────┴──────┴────────┴───────┴──────┴────────┘
```

### Recent Anomalies
```
⚠️  Recent Anomalies (Last 10)

┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Time             ┃ Type           ┃ Severity ┃ Description              ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 2025-01-15 14:20 │ high_cost      │ HIGH     │ Cost $0.0189 exceeds... │
│ 2025-01-15 14:15 │ pii_detected   │ HIGH     │ PII detected: email     │
│ 2025-01-15 14:10 │ cost_spike     │ HIGH     │ Cost spike: 3.2x avg    │
│ 2025-01-15 14:05 │ latency_spike  │ MEDIUM   │ Latency spike: 3.5x avg │
└──────────────────┴────────────────┴──────────┴─────────────────────────┘
```

### Cost Report
```
💰 Cost Report (Last 24 Hours)

Total Cost: $0.4521

By Provider:
┏━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Provider ┃ Requests ┃ Cost     ┃ Avg/Request ┃
┡━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ openai   │       32 │ $0.3456  │ $0.0108     │
│ anthropic│       15 │ $0.1065  │ $0.0071     │
└──────────┴──────────┴──────────┴─────────────┘

By Model:
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Model         ┃ Requests ┃ Cost     ┃ Avg/Request ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ gpt-4         │        7 │ $0.2341  │ $0.0334     │
│ gpt-3.5-turbo │       25 │ $0.1115  │ $0.0045     │
│ claude-haiku  │       15 │ $0.1065  │ $0.0071     │
└───────────────┴──────────┴──────────┴─────────────┘

Hourly Breakdown:
14:00 - 15:00: $0.1234
13:00 - 14:00: $0.0987
12:00 - 13:00: $0.1456
...
```

## 🔧 Export Danych

### Export do JSON
```bash
python cli.py export events.json --hours 24
```

### Export do CSV
```bash
python cli.py export events.csv --format csv --hours 24
```

## 📊 Real-time Monitoring

```bash
# Watch mode - odświeżanie co 5 sekund
python cli.py watch --interval 5
```

## 🔗 Zależności

### Wejście (od)
- Storage Layer - dane do wyświetlenia

## 📖 Więcej Informacji

- [Storage Layer](../components/storage-layer/README.md) - Źródło danych
- [Główny README](../README.md) - Przegląd systemu
