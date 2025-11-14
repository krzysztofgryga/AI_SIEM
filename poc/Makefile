.PHONY: help setup up down restart logs shell test clean stats pull-model

# Default target
.DEFAULT_GOAL := help

# Colors
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)

help: ## Show this help message
	@echo '$(GREEN)AI Monitoring POC - Docker Commands$(RESET)'
	@echo ''
	@echo 'Usage:'
	@echo '  make $(YELLOW)<target>$(RESET)'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-15s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Run initial setup (interactive)
	@chmod +x setup.sh
	@./setup.sh

up: ## Start all services
	docker-compose up -d
	@echo '$(GREEN)✓ Services started$(RESET)'
	@echo ''
	@make status

up-full: ## Start all services including LocalAI and UI
	docker-compose --profile localai --profile ui up -d
	@echo '$(GREEN)✓ All services started$(RESET)'
	@echo ''
	@make status

down: ## Stop all services
	docker-compose down
	@echo '$(GREEN)✓ Services stopped$(RESET)'

restart: ## Restart all services
	docker-compose restart
	@echo '$(GREEN)✓ Services restarted$(RESET)'

logs: ## Show logs (all services)
	docker-compose logs -f

logs-ollama: ## Show Ollama logs
	docker logs -f ai-monitoring-ollama

logs-monitoring: ## Show monitoring logs
	docker logs -f ai-monitoring-poc

status: ## Show status of all services
	@echo '$(GREEN)Services Status:$(RESET)'
	@docker-compose ps
	@echo ''
	@echo '$(GREEN)Available endpoints:$(RESET)'
	@echo '  • Ollama: http://localhost:11434'
	@echo '  • LocalAI: http://localhost:8080 (if started with --profile localai)'
	@echo '  • SQLite UI: http://localhost:8081 (if started with --profile ui)'

shell: ## Open shell in monitoring container
	docker exec -it ai-monitoring-poc bash

python: ## Open Python REPL in monitoring container
	docker exec -it ai-monitoring-poc python

test: ## Run local example
	docker exec -it ai-monitoring-poc python local_example.py

cli: ## Open CLI dashboard
	docker exec -it ai-monitoring-poc python cli.py

stats: ## Show statistics
	docker exec -it ai-monitoring-poc python cli.py stats

events: ## Show recent events
	docker exec -it ai-monitoring-poc python cli.py events 20

anomalies: ## Show anomalies
	docker exec -it ai-monitoring-poc python cli.py anomalies

pull-llama2: ## Pull llama2 model
	docker exec -it ai-monitoring-ollama ollama pull llama2
	@echo '$(GREEN)✓ llama2 model downloaded$(RESET)'

pull-tinyllama: ## Pull tinyllama model (small, fast)
	docker exec -it ai-monitoring-ollama ollama pull tinyllama
	@echo '$(GREEN)✓ tinyllama model downloaded$(RESET)'

pull-mistral: ## Pull mistral model
	docker exec -it ai-monitoring-ollama ollama pull mistral
	@echo '$(GREEN)✓ mistral model downloaded$(RESET)'

list-models: ## List downloaded Ollama models
	docker exec -it ai-monitoring-ollama ollama list

build: ## Build Docker images
	docker-compose build

rebuild: ## Rebuild Docker images from scratch
	docker-compose build --no-cache

clean: ## Stop and remove containers, networks
	docker-compose down
	@echo '$(GREEN)✓ Cleaned up$(RESET)'

clean-all: ## Stop and remove everything including volumes (WARNING: deletes data!)
	@echo '$(YELLOW)⚠ WARNING: This will delete all data!$(RESET)'
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		rm -rf data/* logs/*; \
		echo '$(GREEN)✓ Everything cleaned$(RESET)'; \
	else \
		echo 'Cancelled'; \
	fi

backup: ## Backup database
	@mkdir -p backups
	@cp data/ai_monitoring.db backups/ai_monitoring_$(shell date +%Y%m%d_%H%M%S).db
	@echo '$(GREEN)✓ Database backed up$(RESET)'

restore: ## Restore latest database backup
	@latest=$$(ls -t backups/*.db | head -1); \
	if [ -z "$$latest" ]; then \
		echo '$(YELLOW)No backups found$(RESET)'; \
	else \
		cp $$latest data/ai_monitoring.db; \
		echo '$(GREEN)✓ Database restored from $$latest$(RESET)'; \
	fi

dev: ## Start in development mode (with code mounting)
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

quick-start: ## Quick start: setup + pull model + test
	@make setup
	@echo ''
	@echo '$(YELLOW)Pulling llama2 model...$(RESET)'
	@make pull-llama2
	@echo ''
	@echo '$(YELLOW)Running test...$(RESET)'
	@make test
	@echo ''
	@echo '$(GREEN)✓ Quick start complete!$(RESET)'
	@echo 'Run "make cli" to view dashboard'
