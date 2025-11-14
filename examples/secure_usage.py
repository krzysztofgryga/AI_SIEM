"""
Secure Usage Example - Przykład z danymi wrażliwymi.

Ten przykład pokazuje jak:
1. Wykrywać PII w promptach
2. Routować zapytania z PII do prywatnych backendów
3. Używać różnych poziomów sensitivity
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from components.application_layer.client import MPCClient
from shared.schemas.contracts import SensitivityLevel, ProcessingHint


async def main():
    print("=" * 60)
    print("AI SIEM - Secure Usage Example")
    print("=" * 60)
    print()

    # Utwórz klienta z pełną konfiguracją
    client = MPCClient(
        application_id="secure-example",
        auth_token="demo-token",
        environment="production"
    )

    # Przykład 1: Dane publiczne
    print("📢 Example 1: PUBLIC data (can use any backend)")
    print("-" * 60)
    try:
        result = await client.process(
            prompt="What is HTTPS?",
            sensitivity=SensitivityLevel.PUBLIC,
            processing_hint=ProcessingHint.AUTO
        )
        print(f"Response: {result.get('response', 'N/A')}")
        print(f"Backend: {result.get('backend', 'N/A')}")
        print(f"Cost: ${result.get('cost', 0):.4f}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")

    # Przykład 2: Dane wewnętrzne
    print("🏢 Example 2: INTERNAL data (trusted backends only)")
    print("-" * 60)
    try:
        result = await client.process(
            prompt="Analyze this internal log: ERROR connection timeout",
            sensitivity=SensitivityLevel.INTERNAL,
            processing_hint=ProcessingHint.MODEL_SMALL
        )
        print(f"Response: {result.get('response', 'N/A')}")
        print(f"Backend: {result.get('backend', 'N/A')}")
        print(f"Cost: ${result.get('cost', 0):.4f}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")

    # Przykład 3: Dane wrażliwe
    print("⚠️  Example 3: SENSITIVE data (private backends only)")
    print("-" * 60)
    try:
        result = await client.process(
            prompt="Review this sensitive config: api_key=secret123",
            sensitivity=SensitivityLevel.SENSITIVE,
            processing_hint=ProcessingHint.MODEL_PRIVATE,
            enable_pii_detection=True
        )
        print(f"Response: {result.get('response', 'N/A')}")
        print(f"Backend: {result.get('backend', 'N/A')}")
        print(f"Cost: ${result.get('cost', 0):.4f}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")

    # Przykład 4: Dane z PII (będzie zablokowane dla cloud LLMs)
    print("🔒 Example 4: PII data (on-prem only)")
    print("-" * 60)
    try:
        result = await client.process(
            prompt="My email is john@example.com and phone is 555-123-4567",
            sensitivity=SensitivityLevel.PII,
            processing_hint=ProcessingHint.MODEL_PRIVATE,  # MUST be private!
            enable_pii_detection=True
        )
        print(f"Response: {result.get('response', 'N/A')}")
        print(f"Backend: {result.get('backend', 'N/A')}")
        print(f"Security flags: {result.get('security_flags', {})}")
        print(f"Cost: ${result.get('cost', 0):.4f}\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")

    print("=" * 60)
    print("✓ Secure example completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
