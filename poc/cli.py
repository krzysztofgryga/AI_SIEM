"""
CLI for viewing monitoring data.
"""
import sys
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich import print as rprint
import json

from storage import EventStorage

console = Console()


def print_header():
    """Print CLI header."""
    console.print("""
[bold cyan]╔════════════════════════════════════════╗
║   AI Monitoring Dashboard CLI          ║
╚════════════════════════════════════════╝[/bold cyan]
    """)


def show_statistics(storage: EventStorage):
    """Show overall statistics."""
    stats = storage.get_statistics(hours=24)

    console.print("\n[bold cyan]📊 Statistics (Last 24 Hours)[/bold cyan]\n")

    if not stats or stats.get('total_events', 0) == 0:
        console.print("[yellow]No events found in the last 24 hours.[/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan", width=30)
    table.add_column("Value", justify="right", style="green")

    table.add_row("Total Events", str(stats.get('total_events', 0)))
    table.add_row("Successful", str(stats.get('successful', 0)))
    table.add_row("Failed", str(stats.get('failed', 0)))

    total = stats.get('total_events', 0)
    success_rate = (stats.get('successful', 0) / total * 100) if total > 0 else 0
    table.add_row("Success Rate", f"{success_rate:.1f}%")

    table.add_row("Total Tokens", f"{stats.get('total_tokens', 0):,}")
    table.add_row("Total Cost", f"${stats.get('total_cost', 0):.4f}")

    avg_latency = stats.get('avg_latency', 0)
    table.add_row("Avg Latency", f"{avg_latency:.0f} ms" if avg_latency else "N/A")

    max_latency = stats.get('max_latency', 0)
    table.add_row("Max Latency", f"{max_latency:.0f} ms" if max_latency else "N/A")

    table.add_row("PII Events", str(stats.get('pii_events', 0)))
    table.add_row("Injection Attempts", str(stats.get('injection_events', 0)))
    table.add_row("Anomalies", str(stats.get('anomalies', 0)))

    console.print(table)


def show_recent_events(storage: EventStorage, limit: int = 10):
    """Show recent events."""
    events = storage.get_recent_events(limit=limit)

    console.print(f"\n[bold cyan]📝 Recent Events (Last {limit})[/bold cyan]\n")

    if not events:
        console.print("[yellow]No events found.[/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Time", style="dim", width=19)
    table.add_column("Provider", style="cyan", width=10)
    table.add_column("Model", style="blue", width=20)
    table.add_column("Tokens", justify="right", width=8)
    table.add_column("Cost", justify="right", width=10)
    table.add_column("Latency", justify="right", width=10)
    table.add_column("Status", width=8)
    table.add_column("Risk", width=8)

    for event in events:
        timestamp = event['timestamp'][:19]  # Cut microseconds
        provider = event['provider']
        model = event['model'][:18] + ".." if len(event['model']) > 20 else event['model']
        tokens = str(event['total_tokens']) if event['total_tokens'] else "-"
        cost = f"${event['cost_usd']:.4f}" if event['cost_usd'] else "-"
        latency = f"{event['latency_ms']:.0f}ms" if event['latency_ms'] else "-"

        status_color = "green" if event['success'] else "red"
        status = "✓" if event['success'] else "✗"

        risk_color = {
            'low': 'green',
            'medium': 'yellow',
            'high': 'red',
            'critical': 'bold red'
        }.get(event['risk_level'], 'white')

        table.add_row(
            timestamp,
            provider,
            model,
            tokens,
            cost,
            latency,
            f"[{status_color}]{status}[/{status_color}]",
            f"[{risk_color}]{event['risk_level']}[/{risk_color}]"
        )

    console.print(table)


def show_recent_anomalies(storage: EventStorage, limit: int = 10):
    """Show recent anomalies."""
    anomalies = storage.get_recent_anomalies(limit=limit)

    console.print(f"\n[bold red]⚠️  Recent Anomalies (Last {limit})[/bold red]\n")

    if not anomalies:
        console.print("[green]No anomalies detected. System is healthy! ✓[/green]")
        return

    for anomaly in anomalies:
        severity = anomaly['severity']
        severity_color = {
            'low': 'green',
            'medium': 'yellow',
            'high': 'red',
            'critical': 'bold red'
        }.get(severity, 'white')

        timestamp = anomaly['timestamp'][:19]

        panel = Panel(
            f"[bold]{anomaly['description']}[/bold]\n\n"
            f"Type: {anomaly['anomaly_type']}\n"
            f"Time: {timestamp}\n"
            f"Action: {anomaly['recommended_action'] or 'None'}",
            title=f"[{severity_color}]{severity.upper()}[/{severity_color}]",
            border_style=severity_color
        )
        console.print(panel)


def show_high_risk_events(storage: EventStorage):
    """Show high risk events."""
    high_risk = storage.get_events_by_risk('high', limit=10)
    critical_risk = storage.get_events_by_risk('critical', limit=10)

    all_risk = high_risk + critical_risk

    console.print("\n[bold red]🚨 High Risk Events[/bold red]\n")

    if not all_risk:
        console.print("[green]No high-risk events found. ✓[/green]")
        return

    for event in all_risk[:10]:  # Top 10
        risk_color = "red" if event['risk_level'] == 'high' else "bold red"

        details = []
        if event['has_pii']:
            details.append("[yellow]⚠ PII Detected[/yellow]")
        if event['injection_detected']:
            details.append("[red]⚠ Injection Attempt[/red]")
        if not event['success']:
            details.append("[red]✗ Failed Request[/red]")
        if event['cost_usd'] and event['cost_usd'] > 0.5:
            details.append(f"[yellow]$ High Cost: ${event['cost_usd']:.4f}[/yellow]")

        console.print(Panel(
            f"Model: {event['model']}\n"
            f"Time: {event['timestamp'][:19]}\n"
            f"Details: {' | '.join(details) if details else 'N/A'}\n"
            f"Prompt: {event['prompt'][:100]}..." if event['prompt'] else "",
            title=f"[{risk_color}]{event['risk_level'].upper()} RISK[/{risk_color}]",
            border_style=risk_color
        ))


def interactive_menu(storage: EventStorage):
    """Interactive menu."""
    while True:
        console.print("\n[bold cyan]Choose an option:[/bold cyan]\n")
        console.print("1. View Statistics")
        console.print("2. View Recent Events")
        console.print("3. View Recent Anomalies")
        console.print("4. View High Risk Events")
        console.print("5. Exit")

        choice = console.input("\n[cyan]Enter choice (1-5):[/cyan] ")

        if choice == '1':
            show_statistics(storage)
        elif choice == '2':
            limit = console.input("[cyan]How many events? (default 10):[/cyan] ")
            limit = int(limit) if limit.isdigit() else 10
            show_recent_events(storage, limit)
        elif choice == '3':
            limit = console.input("[cyan]How many anomalies? (default 10):[/cyan] ")
            limit = int(limit) if limit.isdigit() else 10
            show_recent_anomalies(storage, limit)
        elif choice == '4':
            show_high_risk_events(storage)
        elif choice == '5':
            console.print("\n[green]👋 Goodbye![/green]\n")
            break
        else:
            console.print("[red]Invalid choice. Please try again.[/red]")


def main():
    """Main CLI function."""
    print_header()

    storage = EventStorage()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'stats':
            show_statistics(storage)
        elif command == 'events':
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            show_recent_events(storage, limit)
        elif command == 'anomalies':
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            show_recent_anomalies(storage, limit)
        elif command == 'risks':
            show_high_risk_events(storage)
        else:
            console.print(f"[red]Unknown command: {command}[/red]")
            console.print("\nAvailable commands:")
            console.print("  stats - Show statistics")
            console.print("  events [limit] - Show recent events")
            console.print("  anomalies [limit] - Show recent anomalies")
            console.print("  risks - Show high risk events")
    else:
        # Interactive mode
        interactive_menu(storage)

    storage.close()


if __name__ == "__main__":
    main()
