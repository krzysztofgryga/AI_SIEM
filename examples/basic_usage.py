"""
Basic Usage Example - Prosty przykład użycia AI SIEM.

Ten przykład pokazuje jak:
1. Utworzyć klienta SimpleMPCClient
2. Wysłać proste zapytanie
3. Otrzymać odpowiedź
"""
import asyncio
import sys
import os

# Dodaj ścieżkę do komponentów
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from components.application_layer.client import SimpleMPCClient


async def main():
    print("=" * 60)
    print("AI SIEM - Basic Usage Example")
    print("=" * 60)
    print()

    # Krok 1: Utwórz klienta
    print("📋 Creating SimpleMPCClient...")
    client = SimpleMPCClient(
        auth_token="demo-token",
        application_id="basic-example"
    )
    print("✓ Client created\n")

    # Krok 2: Wyślij proste zapytanie
    print("📝 Sending simple query...")
    question = "What is API security?"
    print(f"   Q: {question}")

    try:
        response = await client.ask(question)
        print(f"   A: {response}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

    # Krok 3: Wyślij zapytanie z flagą bezpieczeństwa
    print("🔒 Sending secure query (uses private model)...")
    secure_question = "Explain XSS attacks"
    print(f"   Q: {secure_question}")

    try:
        response = await client.ask(secure_question, use_private_model=True)
        print(f"   A: {response}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

    print("=" * 60)
    print("✓ Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
