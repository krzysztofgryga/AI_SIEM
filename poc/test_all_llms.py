"""
Test script to try all available LLM providers and generate a comparison report.
"""
import asyncio
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from local_collector import OllamaCollector, LMStudioCollector, LocalAICollector
from collector import OpenAICollector, AnthropicCollector, GeminiCollector
from processor import EventProcessor
from storage import EventStorage
from analyzer import AnomalyDetector

console = Console()


class LLMTester:
    """Test multiple LLM providers."""

    def __init__(self):
        self.results = []
        self.processor = EventProcessor()
        self.storage = EventStorage()
        self.analyzer = AnomalyDetector()

    async def handle_event(self, event):
        """Handle event for testing."""
        event = self.processor.process_event(event)
        self.storage.store_event(event)

        self.results.append({
            'provider': event.metadata.get('provider', event.provider.value),
            'model': event.model,
            'success': event.success,
            'latency_ms': event.latency_ms,
            'tokens': event.tokens.total_tokens if event.tokens else 0,
            'cost': event.cost_usd,
            'has_pii': event.has_pii,
            'injection': event.injection_detected,
            'risk': event.risk_level.value
        })

    async def test_ollama(self):
        """Test Ollama."""
        console.print("\n[cyan]Testing Ollama...[/cyan]")

        try:
            ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
            collector = OllamaCollector(
                base_url=ollama_host,
                event_handler=self.handle_event
            )

            await collector.generate(
                model="llama2",
                prompt="What is AI monitoring? Answer in one sentence."
            )

            await collector.close()
            console.print("[green]✓ Ollama working[/green]")
            return True

        except Exception as e:
            console.print(f"[red]✗ Ollama failed: {e}[/red]")
            return False

    async def test_lm_studio(self):
        """Test LM Studio."""
        console.print("\n[cyan]Testing LM Studio...[/cyan]")

        try:
            lm_studio_host = os.getenv('LM_STUDIO_HOST', 'http://localhost:1234')
            collector = LMStudioCollector(
                base_url=lm_studio_host,
                event_handler=self.handle_event
            )

            await collector.chat_completion(
                model="local-model",
                messages=[{"role": "user", "content": "What is AI?"}]
            )

            await collector.close()
            console.print("[green]✓ LM Studio working[/green]")
            return True

        except Exception as e:
            console.print(f"[red]✗ LM Studio failed: {e}[/red]")
            return False

    async def test_localai(self):
        """Test LocalAI."""
        console.print("\n[cyan]Testing LocalAI...[/cyan]")

        try:
            localai_host = os.getenv('LOCALAI_HOST', 'http://localhost:8080')
            collector = LocalAICollector(
                base_url=localai_host,
                event_handler=self.handle_event
            )

            await collector.chat_completion(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}]
            )

            await collector.close()
            console.print("[green]✓ LocalAI working[/green]")
            return True

        except Exception as e:
            console.print(f"[red]✗ LocalAI failed: {e}[/red]")
            return False

    async def test_openai(self):
        """Test OpenAI."""
        if not os.getenv('OPENAI_API_KEY'):
            console.print("[yellow]⊘ OpenAI API key not set, skipping[/yellow]")
            return False

        console.print("\n[cyan]Testing OpenAI...[/cyan]")

        try:
            from openai import OpenAI

            client = OpenAI()
            collector = OpenAICollector(
                client,
                event_handler=self.handle_event
            )

            collector.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "What is 2+2?"}]
            )

            console.print("[green]✓ OpenAI working[/green]")
            return True

        except Exception as e:
            console.print(f"[red]✗ OpenAI failed: {e}[/red]")
            return False

    async def test_anthropic(self):
        """Test Anthropic."""
        if not os.getenv('ANTHROPIC_API_KEY'):
            console.print("[yellow]⊘ Anthropic API key not set, skipping[/yellow]")
            return False

        console.print("\n[cyan]Testing Anthropic...[/cyan]")

        try:
            from anthropic import Anthropic

            client = Anthropic()
            collector = AnthropicCollector(
                client,
                event_handler=self.handle_event
            )

            collector.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                messages=[{"role": "user", "content": "What is 2+2?"}]
            )

            console.print("[green]✓ Anthropic working[/green]")
            return True

        except Exception as e:
            console.print(f"[red]✗ Anthropic failed: {e}[/red]")
            return False

    async def test_gemini(self):
        """Test Google Gemini."""
        if not os.getenv('GOOGLE_API_KEY'):
            console.print("[yellow]⊘ Google API key not set, skipping[/yellow]")
            return False

        console.print("\n[cyan]Testing Google Gemini...[/cyan]")

        try:
            import google.generativeai as genai

            genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
            model = genai.GenerativeModel('gemini-pro')

            collector = GeminiCollector(
                model,
                event_handler=self.handle_event
            )

            collector.model.generate_content("What is 2+2?")

            console.print("[green]✓ Google Gemini working[/green]")
            return True

        except Exception as e:
            console.print(f"[red]✗ Google Gemini failed: {e}[/red]")
            return False

    def print_results(self):
        """Print comparison table."""
        if not self.results:
            console.print("\n[yellow]No results to display[/yellow]")
            return

        console.print("\n")
        table = Table(title="LLM Provider Comparison", show_header=True, header_style="bold magenta")

        table.add_column("Provider", style="cyan")
        table.add_column("Model", style="blue")
        table.add_column("Status", style="green")
        table.add_column("Latency", justify="right")
        table.add_column("Tokens", justify="right")
        table.add_column("Cost", justify="right")
        table.add_column("Risk", justify="center")

        for result in self.results:
            status = "✓" if result['success'] else "✗"
            status_color = "green" if result['success'] else "red"

            risk_color = {
                'low': 'green',
                'medium': 'yellow',
                'high': 'red',
                'critical': 'bold red'
            }.get(result['risk'], 'white')

            table.add_row(
                result['provider'],
                result['model'],
                f"[{status_color}]{status}[/{status_color}]",
                f"{result['latency_ms']:.0f}ms",
                str(result['tokens']),
                f"${result['cost']:.4f}",
                f"[{risk_color}]{result['risk']}[/{risk_color}]"
            )

        console.print(table)

        # Summary
        total_tests = len(self.results)
        successful = sum(1 for r in self.results if r['success'])
        avg_latency = sum(r['latency_ms'] for r in self.results) / total_tests if total_tests else 0
        total_cost = sum(r['cost'] for r in self.results)

        console.print("\n[bold cyan]Summary:[/bold cyan]")
        console.print(f"  Providers tested: {total_tests}")
        console.print(f"  Successful: {successful}/{total_tests}")
        console.print(f"  Avg latency: {avg_latency:.0f}ms")
        console.print(f"  Total cost: ${total_cost:.4f}")
        console.print(f"\n💾 Results saved to database")


async def main():
    """Main test function."""
    console.print("""
[bold cyan]╔════════════════════════════════════════╗
║   LLM Provider Testing Suite           ║
╚════════════════════════════════════════╝[/bold cyan]
    """)

    tester = LLMTester()

    console.print("\n[bold]Testing available LLM providers...[/bold]")
    console.print("This will test each provider with a simple query.\n")

    # Test all providers
    await tester.test_ollama()
    await tester.test_lm_studio()
    await tester.test_localai()
    await tester.test_openai()
    await tester.test_anthropic()
    await tester.test_gemini()

    # Wait for async processing
    await asyncio.sleep(1)

    # Show results
    tester.print_results()

    # Recommendations
    console.print("\n[bold cyan]Recommendations:[/bold cyan]")

    working_providers = [r for r in tester.results if r['success']]
    if not working_providers:
        console.print("[red]No providers working! Please set up at least one:[/red]")
        console.print("  • Ollama: https://ollama.ai/download")
        console.print("  • LM Studio: https://lmstudio.ai/")
        console.print("  • OpenAI API key")
    else:
        # Find cheapest
        free_providers = [r for r in working_providers if r['cost'] == 0]
        if free_providers:
            fastest_free = min(free_providers, key=lambda x: x['latency_ms'])
            console.print(f"[green]Best option (free + fast): {fastest_free['provider']} ({fastest_free['latency_ms']:.0f}ms)[/green]")

        # Find fastest
        fastest = min(working_providers, key=lambda x: x['latency_ms'])
        console.print(f"[cyan]Fastest: {fastest['provider']} ({fastest['latency_ms']:.0f}ms)[/cyan]")

        # Find cheapest paid
        paid_providers = [r for r in working_providers if r['cost'] > 0]
        if paid_providers:
            cheapest = min(paid_providers, key=lambda x: x['cost'])
            console.print(f"[yellow]Cheapest paid: {cheapest['provider']} (${cheapest['cost']:.4f})[/yellow]")

    console.print()


if __name__ == "__main__":
    asyncio.run(main())
