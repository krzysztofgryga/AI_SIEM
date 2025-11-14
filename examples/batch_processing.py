"""
Batch Processing Example - Przetwarzanie wielu zapytań.

Ten przykład pokazuje jak:
1. Przetwarzać wiele zapytań jednocześnie
2. Zbierać metryki dla całej partii
3. Optymalizować koszty przez wybór backendów
"""
import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from components.application_layer.client import SimpleMPCClient


async def main():
    print("=" * 60)
    print("AI SIEM - Batch Processing Example")
    print("=" * 60)
    print()

    client = SimpleMPCClient(auth_token="demo-token")

    # Przygotuj listę zapytań
    questions = [
        "What is SQL injection?",
        "Explain XSS attacks",
        "What is CSRF?",
        "How does JWT authentication work?",
        "What are API rate limits?",
        "Explain CORS policy",
        "What is OAuth 2.0?",
        "How does TLS work?",
        "What is API versioning?",
        "Explain REST vs GraphQL"
    ]

    print(f"📝 Processing {len(questions)} questions...")
    print()

    # Pomiar czasu
    start_time = time.time()

    # Przetwórz wszystkie zapytania
    print("Processing:")
    for i, question in enumerate(questions, 1):
        print(f"  {i}. {question}")

    print("\nExecuting batch...")
    try:
        results = await client.client.batch_process(questions)

        # Oblicz metryki
        total_time = time.time() - start_time
        total_cost = sum(r.get('cost', 0) for r in results)
        avg_cost = total_cost / len(results)

        print("\n" + "=" * 60)
        print("📊 Batch Results")
        print("=" * 60)
        print(f"Total questions: {len(questions)}")
        print(f"Successful: {len(results)}")
        print(f"Total time: {total_time:.2f}s")
        print(f"Avg time per question: {total_time/len(results):.2f}s")
        print(f"Total cost: ${total_cost:.4f}")
        print(f"Avg cost per question: ${avg_cost:.4f}")
        print()

        # Wyświetl pierwsze 3 odpowiedzi
        print("Sample Responses (first 3):")
        print("-" * 60)
        for i, (q, r) in enumerate(zip(questions[:3], results[:3]), 1):
            response_text = r.get('response', 'N/A')
            if len(response_text) > 100:
                response_text = response_text[:100] + "..."
            print(f"\n{i}. Q: {q}")
            print(f"   A: {response_text}")
            print(f"   Backend: {r.get('backend', 'N/A')}")
            print(f"   Cost: ${r.get('cost', 0):.4f}")

    except Exception as e:
        print(f"\n❌ Batch processing failed: {e}")

    print("\n" + "=" * 60)
    print("✓ Batch processing example completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
