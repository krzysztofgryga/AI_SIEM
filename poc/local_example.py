"""
Example usage with local LLM servers (Ollama, LM Studio, LocalAI).

This example works WITHOUT any API keys - completely local!
"""
import asyncio
import os
from rich.console import Console

from local_collector import OllamaCollector, LMStudioCollector, LocalAICollector
from processor import EventProcessor
from storage import EventStorage
from analyzer import AnomalyDetector

console = Console()


async def handle_event(event):
    """Handle incoming events."""
    processor = EventProcessor()
    storage = EventStorage()
    analyzer = AnomalyDetector()

    # Process
    event = processor.process_event(event)

    # Store
    storage.store_event(event)

    # Analyze
    anomalies = analyzer.analyze_event(event, [])

    # Print event
    console.print(f"\n📝 Event: {event.model} - {event.tokens.total_tokens if event.tokens else 0} tokens - {event.latency_ms:.0f}ms")

    # Print anomalies
    for anomaly in anomalies:
        storage.store_anomaly(anomaly)
        if anomaly.severity.value in ['critical', 'high']:
            console.print(f"🚨 {anomaly.severity.value.upper()}: {anomaly.description}")

    storage.close()


async def example_ollama():
    """Example with Ollama."""
    console.print("\n[bold cyan]🦙 Ollama Example[/bold cyan]\n")

    # Get Ollama host from env or use default
    ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')

    collector = OllamaCollector(
        base_url=ollama_host,
        event_handler=handle_event,
        user_id="local_user"
    )

    try:
        console.print(f"[cyan]Connecting to Ollama at {ollama_host}...[/cyan]")

        # Example 1: Simple generation
        console.print("\n[yellow]1. Simple generation with llama2[/yellow]")
        result = await collector.generate(
            model="llama2",
            prompt="What is 2+2? Answer briefly."
        )
        console.print(f"Response: {result['response'][:200]}")

        # Example 2: Chat
        console.print("\n[yellow]2. Chat with llama2[/yellow]")
        result = await collector.chat(
            model="llama2",
            messages=[
                {"role": "user", "content": "Tell me a joke about programming"}
            ]
        )
        message = result.get('message', {})
        console.print(f"Response: {message.get('content', '')[:200]}")

        # Example 3: With potential PII (to test detection)
        console.print("\n[yellow]3. Testing PII detection[/yellow]")
        result = await collector.generate(
            model="llama2",
            prompt="My email is test@example.com, can you help me?"
        )
        console.print(f"Response: {result['response'][:200]}")

        await collector.close()

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print(f"\n[yellow]Make sure Ollama is running:[/yellow]")
        console.print(f"  1. Install: https://ollama.ai/download")
        console.print(f"  2. Pull model: ollama pull llama2")
        console.print(f"  3. Start: ollama serve")


async def example_lm_studio():
    """Example with LM Studio."""
    console.print("\n[bold cyan]🎨 LM Studio Example[/bold cyan]\n")

    lm_studio_host = os.getenv('LM_STUDIO_HOST', 'http://localhost:1234')

    collector = LMStudioCollector(
        base_url=lm_studio_host,
        event_handler=handle_event,
        user_id="local_user"
    )

    try:
        console.print(f"[cyan]Connecting to LM Studio at {lm_studio_host}...[/cyan]")

        result = await collector.chat_completion(
            model="local-model",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is Python?"}
            ]
        )

        choice = result.get('choices', [{}])[0]
        message = choice.get('message', {})
        console.print(f"Response: {message.get('content', '')[:200]}")

        await collector.close()

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print(f"\n[yellow]Make sure LM Studio is running:[/yellow]")
        console.print(f"  1. Download: https://lmstudio.ai/")
        console.print(f"  2. Load a model")
        console.print(f"  3. Start local server (default port 1234)")


async def example_localai():
    """Example with LocalAI."""
    console.print("\n[bold cyan]🤖 LocalAI Example[/bold cyan]\n")

    localai_host = os.getenv('LOCALAI_HOST', 'http://localhost:8080')

    collector = LocalAICollector(
        base_url=localai_host,
        event_handler=handle_event,
        user_id="local_user"
    )

    try:
        console.print(f"[cyan]Connecting to LocalAI at {localai_host}...[/cyan]")

        result = await collector.chat_completion(
            model="gpt-3.5-turbo",  # LocalAI model name
            messages=[
                {"role": "user", "content": "Hello, who are you?"}
            ]
        )

        choice = result.get('choices', [{}])[0]
        message = choice.get('message', {})
        console.print(f"Response: {message.get('content', '')[:200]}")

        await collector.close()

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print(f"\n[yellow]Make sure LocalAI is running:[/yellow]")
        console.print(f"  Docker: docker run -p 8080:8080 quay.io/go-skynet/local-ai:latest")


async def main():
    """Main function."""
    console.print("""
[bold cyan]╔════════════════════════════════════════╗
║   AI Monitoring - Local LLM Demo      ║
║   NO API KEYS REQUIRED!                ║
╚════════════════════════════════════════╝[/bold cyan]
    """)

    # Check what's available
    console.print("\n[bold]Available local LLM servers:[/bold]")
    console.print("  1. Ollama (http://localhost:11434)")
    console.print("  2. LM Studio (http://localhost:1234)")
    console.print("  3. LocalAI (http://localhost:8080)")
    console.print("\nTrying to connect...\n")

    # Try Ollama first (most common)
    try:
        await example_ollama()
    except Exception:
        pass

    # # Uncomment to test LM Studio
    # try:
    #     await example_lm_studio()
    # except Exception:
    #     pass

    # # Uncomment to test LocalAI
    # try:
    #     await example_localai()
    # except Exception:
    #     pass

    # Show summary
    console.print("\n" + "="*50)
    storage = EventStorage()
    stats = storage.get_statistics(hours=1)

    console.print("\n[bold cyan]📊 Summary:[/bold cyan]")
    console.print(f"  Total requests: {stats.get('total_events', 0)}")
    console.print(f"  Avg latency: {stats.get('avg_latency', 0):.0f}ms")
    console.print(f"  Total tokens: {stats.get('total_tokens', 0)}")
    console.print(f"  PII detected: {stats.get('pii_events', 0)}")
    console.print(f"  Injections: {stats.get('injection_events', 0)}")
    console.print(f"  Anomalies: {stats.get('anomalies', 0)}")
    console.print(f"\n💾 Data saved to: ai_monitoring.db")
    console.print("📊 Run 'python cli.py' to view details\n")

    storage.close()


if __name__ == "__main__":
    asyncio.run(main())
