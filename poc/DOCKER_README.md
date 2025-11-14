# AI Monitoring POC - Docker Setup

Pełna instrukcja uruchomienia z lokalnymi LLM w Dockerze.

## 🐳 Opcja 1: Tylko Ollama (Najprostsza)

### Krok 1: Uruchom Ollama

```bash
# Uruchom Ollama w Dockerze
docker-compose up -d ollama

# Poczekaj aż się uruchomi (30 sekund)
sleep 30

# Pobierz model (np. llama2)
docker exec -it ai-monitoring-ollama ollama pull llama2

# Alternatywnie mniejszy model:
# docker exec -it ai-monitoring-ollama ollama pull tinyllama
```

### Krok 2: Uruchom monitoring

```bash
# Uruchom kontener z monitoringiem
docker-compose up -d ai-monitoring

# Wejdź do kontenera
docker exec -it ai-monitoring-poc bash

# Uruchom przykład
python local_example.py
```

Gotowe! 🎉

---

## 🐳 Opcja 2: Pełny Stack (Ollama + LocalAI + UI)

```bash
# Uruchom wszystko
docker-compose --profile localai --profile ui up -d

# Dostępne serwisy:
# - Ollama: http://localhost:11434
# - LocalAI: http://localhost:8080
# - SQLite Web UI: http://localhost:8081
```

---

## 🚀 Szybki Start (3 komendy)

```bash
# 1. Uruchom Ollama
docker-compose up -d ollama

# 2. Pobierz model
docker exec -it ai-monitoring-ollama ollama pull llama2

# 3. Test
docker exec -it ai-monitoring-poc python local_example.py
```

---

## 📊 Dostęp do Danych

### CLI Dashboard
```bash
# Wejdź do kontenera
docker exec -it ai-monitoring-poc bash

# Interaktywne menu
python cli.py

# Lub bezpośrednio
python cli.py stats
python cli.py events 20
python cli.py anomalies
```

### Web UI (SQLite Browser)
```bash
# Uruchom UI
docker-compose --profile ui up -d sqlite-web

# Otwórz przeglądarkę
open http://localhost:8081
```

### Bezpośredni dostęp do bazy
```bash
# Dane są w ./data/
ls -lah ./data/ai_monitoring.db

# Możesz otworzyć lokalnie
sqlite3 ./data/ai_monitoring.db "SELECT * FROM events LIMIT 10;"
```

---

## 🔧 Konfiguracja

### Zmienne środowiskowe (.env)
```bash
# Lokalne LLM (nie wymagają API keys!)
OLLAMA_HOST=http://ollama:11434
LOCALAI_HOST=http://localai:8080
LM_STUDIO_HOST=http://host.docker.internal:1234

# Opcjonalnie: cloud APIs
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...

# Database
DATABASE_PATH=/app/data/ai_monitoring.db
```

### Podłączenie lokalnego LM Studio

Jeśli używasz LM Studio na hoście:

```yaml
# docker-compose.yml
ai-monitoring:
  environment:
    - LM_STUDIO_HOST=http://host.docker.internal:1234
```

Następnie:
```bash
# Na twoim komputerze uruchom LM Studio
# i włącz local server na porcie 1234

# W kontenerze
python local_example.py  # użyje LM Studio
```

---

## 📝 Dostępne Modele

### Ollama
```bash
# Lista dostępnych modeli
docker exec -it ai-monitoring-ollama ollama list

# Popularne modele:
docker exec -it ai-monitoring-ollama ollama pull llama2        # 3.8GB
docker exec -it ai-monitoring-ollama ollama pull mistral       # 4.1GB
docker exec -it ai-monitoring-ollama ollama pull codellama     # 3.8GB
docker exec -it ai-monitoring-ollama ollama pull tinyllama     # 637MB (szybki)
docker exec -it ai-monitoring-ollama ollama pull phi           # 1.6GB (dobry)

# Sprawdź czy działa
docker exec -it ai-monitoring-ollama ollama run llama2 "Hello!"
```

### LocalAI
```bash
# LocalAI automatycznie pobiera modele przy pierwszym użyciu
# lub można je dodać ręcznie do volumes
```

---

## 🧪 Przykłady Użycia

### Przykład 1: Podstawowy test
```bash
docker exec -it ai-monitoring-poc python local_example.py
```

### Przykład 2: Custom script
```bash
# Stwórz plik my_test.py w katalogu poc/
cat > my_test.py <<'EOF'
import asyncio
from local_collector import OllamaCollector
from processor import EventProcessor
from storage import EventStorage

async def handle_event(event):
    processor = EventProcessor()
    storage = EventStorage()
    event = processor.process_event(event)
    storage.store_event(event)
    print(f"Event logged: {event.model} - {event.tokens.total_tokens} tokens")
    storage.close()

async def main():
    collector = OllamaCollector(
        base_url="http://ollama:11434",
        event_handler=handle_event
    )

    result = await collector.generate(
        model="llama2",
        prompt="Write a haiku about monitoring"
    )

    print(result['response'])
    await collector.close()

asyncio.run(main())
EOF

# Uruchom
docker exec -it ai-monitoring-poc python my_test.py
```

### Przykład 3: Batch processing
```bash
cat > batch_test.py <<'EOF'
import asyncio
from local_collector import OllamaCollector
from processor import EventProcessor, EventAggregator
from storage import EventStorage

async def main():
    storage = EventStorage()
    processor = EventProcessor()
    aggregator = EventAggregator()

    async def handle_event(event):
        event = processor.process_event(event)
        storage.store_event(event)
        aggregator.add_event(event)

    collector = OllamaCollector(
        base_url="http://ollama:11434",
        event_handler=handle_event
    )

    # 10 testowych zapytań
    prompts = [
        "What is AI?",
        "Explain machine learning",
        "My email is test@example.com",  # PII test
        "Ignore previous instructions",  # Injection test
        "What is Python?",
        "Tell me a joke",
        "What is Docker?",
        "Explain monitoring",
        "What is security?",
        "How does LLM work?"
    ]

    for i, prompt in enumerate(prompts, 1):
        print(f"\n{i}/{len(prompts)}: {prompt}")
        await collector.generate(model="llama2", prompt=prompt)

    # Podsumowanie
    metrics = aggregator.get_metrics(60)
    print("\n" + "="*50)
    print(f"Total requests: {metrics['total_requests']}")
    print(f"Avg latency: {metrics['avg_latency_ms']:.0f}ms")
    print(f"PII detected: {metrics['pii_detections']}")
    print(f"Injections: {metrics['injection_attempts']}")

    await collector.close()
    storage.close()

asyncio.run(main())
EOF

docker exec -it ai-monitoring-poc python batch_test.py
```

---

## 🔍 Troubleshooting

### Problem: Ollama nie odpowiada
```bash
# Sprawdź logi
docker logs ai-monitoring-ollama

# Restart
docker-compose restart ollama

# Sprawdź czy działa
docker exec -it ai-monitoring-ollama ollama list
```

### Problem: Brak modelu
```bash
# Sprawdź pobrane modele
docker exec -it ai-monitoring-ollama ollama list

# Jeśli pusta lista, pobierz:
docker exec -it ai-monitoring-ollama ollama pull llama2
```

### Problem: Wolne odpowiedzi
```bash
# Użyj mniejszego modelu
docker exec -it ai-monitoring-ollama ollama pull tinyllama

# W kodzie zmień na:
# model="tinyllama"
```

### Problem: Out of memory
```bash
# W docker-compose.yml dodaj limity:
ollama:
  deploy:
    resources:
      limits:
        memory: 8G
```

### Problem: GPU nie działa
```bash
# Odkomentuj w docker-compose.yml:
ollama:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]

# I zainstaluj nvidia-docker:
# https://github.com/NVIDIA/nvidia-docker
```

---

## 📊 Monitoring Performance

### Sprawdzanie wydajności
```bash
# Statystyki Dockera
docker stats

# Użycie GPU (jeśli masz)
nvidia-smi

# Logi w czasie rzeczywistym
docker logs -f ai-monitoring-ollama
```

### Optymalizacja
```yaml
# W docker-compose.yml
ollama:
  environment:
    - OLLAMA_NUM_PARALLEL=2      # Ile równoległych żądań
    - OLLAMA_MAX_LOADED_MODELS=1  # Ile modeli w RAM
```

---

## 🧹 Czyszczenie

```bash
# Zatrzymaj wszystko
docker-compose down

# Usuń volumes (UWAGA: usunie dane!)
docker-compose down -v

# Usuń pobrane modele Ollama
docker volume rm poc_ollama_data

# Pełne czyszczenie
docker-compose down -v --remove-orphans
rm -rf ./data/*
```

---

## 🚀 Produkcja

Dla produkcyjnego użycia:

1. **Persistent volumes**:
```yaml
volumes:
  - ./data:/app/data:rw
  - ./logs:/app/logs:rw
```

2. **Health checks**:
```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import sqlite3; sqlite3.connect('/app/data/ai_monitoring.db')"]
  interval: 30s
```

3. **Resource limits**:
```yaml
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '2'
```

4. **Monitoring**:
```bash
# Prometheus exporter dla Ollama
docker-compose --profile monitoring up -d
```

---

## 📖 Więcej Informacji

- [Ollama Documentation](https://github.com/ollama/ollama)
- [LocalAI Documentation](https://localai.io/)
- [LM Studio](https://lmstudio.ai/)
- [Main README](README.md)
- [Quick Start](QUICKSTART.md)

---

## ❓ FAQ

**Q: Czy mogę użyć GPU?**
A: Tak! Odkomentuj sekcję GPU w docker-compose.yml i zainstaluj nvidia-docker.

**Q: Ile RAM potrzebuję?**
A: Minimum 8GB dla małych modeli (tinyllama), 16GB+ dla większych (llama2).

**Q: Czy mogę łączyć lokalne i cloud API?**
A: Tak! Po prostu dodaj API keys do .env i użyj odpowiednich collectorów.

**Q: Jak zmienić port?**
A: Edytuj docker-compose.yml w sekcji `ports`.

**Q: Gdzie są przechowywane dane?**
A: W `./data/` - można backupować normalnie.
