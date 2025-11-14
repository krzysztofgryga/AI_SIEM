# Docker Quick Start - 2 minuty do działającego systemu! 🚀

## Automatyczny Setup (Najprostsze)

```bash
# 1. Uruchom setup
make setup

# 2. Gotowe! 🎉
```

To wszystko! Skrypt:
- Uruchomi Ollama
- Pobierze model (llama2/tinyllama/mistral)
- Uruchomi monitoring
- Pokaże przykłady użycia

---

## Ręczny Setup (3 komendy)

```bash
# 1. Uruchom serwisy
make up

# 2. Pobierz model
make pull-llama2

# 3. Testuj
make test
```

---

## Podstawowe Komendy

```bash
# Uruchomienie
make up              # Start podstawowych serwisów
make up-full         # Start wszystkiego (+ UI)

# Testowanie
make test            # Uruchom przykład
make cli             # Dashboard CLI
make stats           # Pokaż statystyki

# Zarządzanie
make logs            # Zobacz logi
make shell           # Wejdź do kontenera
make down            # Zatrzymaj wszystko

# Modele
make pull-llama2     # Pobierz llama2
make pull-tinyllama  # Pobierz tinyllama (mały, szybki)
make list-models     # Pokaż pobrane modele

# Pomoc
make help            # Wszystkie komendy
```

---

## Przykłady Użycia

### 1. Szybki test
```bash
make test
```

Output:
```
🦙 Ollama Example

Connecting to Ollama at http://ollama:11434...

1. Simple generation with llama2
📝 Event: llama2 - 28 tokens - 1234ms
Response: 2 + 2 equals 4.
```

### 2. Dashboard
```bash
make cli
```

Interaktywne menu:
```
Choose an option:

1. View Statistics
2. View Recent Events
3. View Recent Anomalies
4. View High Risk Events
5. Exit

Enter choice (1-5):
```

### 3. Custom script
```bash
# Wejdź do kontenera
make shell

# Stwórz swój skrypt
cat > my_test.py <<'EOF'
import asyncio
from local_collector import OllamaCollector

async def main():
    collector = OllamaCollector(base_url="http://ollama:11434")
    result = await collector.generate(
        model="llama2",
        prompt="Write a haiku about AI"
    )
    print(result['response'])

asyncio.run(main())
EOF

# Uruchom
python my_test.py
```

---

## Dostępne Serwisy

Po `make up`:

| Serwis | URL | Opis |
|--------|-----|------|
| Ollama | http://localhost:11434 | Lokalny LLM server |
| Monitoring | (container) | System monitoringu |

Po `make up-full`:

| Serwis | URL | Opis |
|--------|-----|------|
| Ollama | http://localhost:11434 | Lokalny LLM server |
| LocalAI | http://localhost:8080 | Alternatywny LLM server |
| SQLite UI | http://localhost:8081 | Przeglądarka bazy danych |
| Monitoring | (container) | System monitoringu |

---

## Modele Ollama

| Model | Rozmiar | Szybkość | Jakość | Komenda |
|-------|---------|----------|--------|---------|
| tinyllama | 637MB | ⚡⚡⚡ | ⭐⭐ | `make pull-tinyllama` |
| llama2 | 3.8GB | ⚡⚡ | ⭐⭐⭐ | `make pull-llama2` |
| mistral | 4.1GB | ⚡⚡ | ⭐⭐⭐⭐ | `make pull-mistral` |

**Rekomendacja**:
- Słaby PC: `tinyllama`
- Normalny: `llama2`
- Mocny: `mistral`

---

## Troubleshooting

### Problem: `make: command not found`
```bash
# Użyj bezpośrednio docker-compose
docker-compose up -d
```

### Problem: Ollama nie odpowiada
```bash
# Restart
make restart

# Sprawdź logi
make logs-ollama
```

### Problem: Wolne odpowiedzi
```bash
# Użyj mniejszego modelu
make pull-tinyllama

# W kodzie zmień na model="tinyllama"
```

### Problem: Brak miejsca
```bash
# Usuń nieużywane modele
docker exec -it ai-monitoring-ollama ollama rm <model-name>

# Wyczyść Docker
docker system prune -a
```

---

## Co Dalej?

1. **Przeczytaj pełną dokumentację**: [DOCKER_README.md](DOCKER_README.md)
2. **Zobacz przykłady**: [local_example.py](local_example.py)
3. **Główny README**: [README.md](README.md)

---

## Cheat Sheet

```bash
# Kompletny workflow
make setup           # Pierwszy raz
make test            # Test
make stats           # Statystyki
make cli             # Dashboard
make down            # Koniec

# Debug
make logs            # Zobacz co się dzieje
make shell           # Wejdź do środka
make status          # Status serwisów

# Czyszczenie
make clean           # Zatrzymaj
make clean-all       # Usuń WSZYSTKO (ostrożnie!)
make backup          # Backup bazy przed usunięciem
```

---

**🎉 To wszystko! Masz działający system monitoringu AI bez żadnych API keys!**

Potrzebujesz pomocy? Zobacz:
- `make help` - lista komend
- [DOCKER_README.md](DOCKER_README.md) - pełna dokumentacja
- [Issues](https://github.com/krzysztofgryga/AI_SIEM/issues) - zgłoś problem
