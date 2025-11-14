#!/bin/bash
# Quick setup script for AI Monitoring POC with Docker

set -e

echo "🤖 AI Monitoring POC - Docker Setup"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker is installed${NC}"
echo -e "${GREEN}✓ Docker Compose is installed${NC}"
echo ""

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Create .env if not exists
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file..."
    cat > .env <<EOF
# Local LLM endpoints (no API keys needed!)
OLLAMA_HOST=http://ollama:11434
LOCALAI_HOST=http://localai:8080
LM_STUDIO_HOST=http://host.docker.internal:1234

# Optional: Cloud API keys (if you want to use them)
# OPENAI_API_KEY=sk-your-key-here
# ANTHROPIC_API_KEY=sk-ant-your-key-here

# Database
DATABASE_PATH=/app/data/ai_monitoring.db
DEFAULT_USER_ID=local_user
EOF
    echo -e "${GREEN}✓ .env file created${NC}"
else
    echo -e "${YELLOW}⚠ .env file already exists, skipping${NC}"
fi
echo ""

# Ask user what to setup
echo "What would you like to setup?"
echo "1) Ollama only (recommended for most users)"
echo "2) Ollama + LocalAI"
echo "3) Full stack (Ollama + LocalAI + SQLite Web UI)"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        PROFILE=""
        ;;
    2)
        PROFILE="--profile localai"
        ;;
    3)
        PROFILE="--profile localai --profile ui"
        ;;
    *)
        echo -e "${RED}Invalid choice, using Ollama only${NC}"
        PROFILE=""
        ;;
esac

# Start services
echo ""
echo "🚀 Starting services..."
docker-compose $PROFILE up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if Ollama is running
if docker ps | grep -q "ai-monitoring-ollama"; then
    echo -e "${GREEN}✓ Ollama is running${NC}"

    # Ask to pull model
    echo ""
    echo "📥 Would you like to pull a model for Ollama?"
    echo "1) llama2 (3.8GB - recommended)"
    echo "2) tinyllama (637MB - fast, smaller)"
    echo "3) mistral (4.1GB - high quality)"
    echo "4) Skip for now"
    echo ""
    read -p "Enter choice [1-4]: " model_choice

    case $model_choice in
        1)
            MODEL="llama2"
            ;;
        2)
            MODEL="tinyllama"
            ;;
        3)
            MODEL="mistral"
            ;;
        *)
            MODEL=""
            ;;
    esac

    if [ ! -z "$MODEL" ]; then
        echo ""
        echo "📥 Pulling $MODEL model (this may take a few minutes)..."
        docker exec ai-monitoring-ollama ollama pull $MODEL
        echo -e "${GREEN}✓ Model $MODEL downloaded${NC}"
    fi
else
    echo -e "${RED}❌ Ollama is not running${NC}"
fi

echo ""
echo "======================================"
echo -e "${GREEN}✅ Setup complete!${NC}"
echo "======================================"
echo ""
echo "📊 Available services:"
echo "  • Ollama: http://localhost:11434"

if [[ $PROFILE == *"localai"* ]]; then
    echo "  • LocalAI: http://localhost:8080"
fi

if [[ $PROFILE == *"ui"* ]]; then
    echo "  • SQLite Web UI: http://localhost:8081"
fi

echo ""
echo "🎯 Next steps:"
echo ""
echo "1. Run example:"
echo "   docker exec -it ai-monitoring-poc python local_example.py"
echo ""
echo "2. View dashboard:"
echo "   docker exec -it ai-monitoring-poc python cli.py"
echo ""
echo "3. Interactive shell:"
echo "   docker exec -it ai-monitoring-poc bash"
echo ""
echo "4. View logs:"
echo "   docker logs -f ai-monitoring-poc"
echo ""
echo "5. Stop services:"
echo "   docker-compose down"
echo ""
echo "📖 For more info, see DOCKER_README.md"
echo ""
