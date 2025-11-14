"""
Example usage of the new 3-layer architecture.

This demonstrates how an application uses the MPC Client to interact
with the AI SIEM system.
"""
import asyncio
import logging
from datetime import datetime

from application.client import MPCClient, SimpleMPCClient
from schemas.contracts import SensitivityLevel, ProcessingHint
from security.auth import AccessControl, Permission, Role


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def example_basic_usage():
    """Example 1: Basic usage with default settings."""
    print("\n" + "="*80)
    print("Example 1: Basic Usage")
    print("="*80)

    # Create a simple client
    client = SimpleMPCClient(
        auth_token="example-token",
        application_id="example-app"
    )

    # Ask a question
    question = "What are the best practices for API security?"
    print(f"\nQuestion: {question}")

    response = await client.ask(question)
    print(f"Response: {response}\n")


async def example_pii_handling():
    """Example 2: Handling PII data."""
    print("\n" + "="*80)
    print("Example 2: PII Handling")
    print("="*80)

    client = SimpleMPCClient()

    # Question with PII
    question_with_pii = (
        "My email is john.doe@example.com and my phone is 555-123-4567. "
        "Can you help me with my account?"
    )

    print(f"\nQuestion (with PII): {question_with_pii}")

    # Use secure mode
    response = await client.ask_secure(
        question_with_pii,
        contains_pii=True
    )

    print(f"Response: {response}")
    print("\nNote: PII was detected and routed to private model\n")


async def example_sensitivity_levels():
    """Example 3: Different sensitivity levels."""
    print("\n" + "="*80)
    print("Example 3: Sensitivity Levels")
    print("="*80)

    client = MPCClient(
        application_id="security-app",
        auth_token="security-token"
    )

    # Test different sensitivity levels
    test_cases = [
        ("Public data", "What is the capital of France?", SensitivityLevel.PUBLIC),
        ("Internal data", "Analyze this internal log file", SensitivityLevel.INTERNAL),
        ("Sensitive data", "Review this customer complaint", SensitivityLevel.SENSITIVE),
    ]

    for name, prompt, sensitivity in test_cases:
        print(f"\n{name} (Sensitivity: {sensitivity.value})")
        print(f"Prompt: {prompt}")

        try:
            result = await client.process(
                prompt=prompt,
                sensitivity=sensitivity,
                processing_hint=ProcessingHint.AUTO
            )

            print(f"Backend: {result.get('backend', 'unknown')}")
            print(f"Response: {result.get('response', '')[:100]}...")

        except Exception as e:
            print(f"Error: {str(e)}")


async def example_processing_hints():
    """Example 4: Using processing hints for routing control."""
    print("\n" + "="*80)
    print("Example 4: Processing Hints")
    print("="*80)

    client = MPCClient(application_id="analytics-app")

    prompt = "Classify this text: 'Error: Connection timeout after 30 seconds'"

    # Try different processing hints
    hints = [
        (ProcessingHint.RULE_ENGINE, "Rule-based (fast, deterministic)"),
        (ProcessingHint.MODEL_SMALL, "Small model (cheap)"),
        (ProcessingHint.MODEL_LARGE, "Large model (expensive, high quality)"),
        (ProcessingHint.HYBRID, "Hybrid (rules + LLM fallback)"),
    ]

    for hint, description in hints:
        print(f"\n{description}")
        print(f"Hint: {hint.value}")

        try:
            result = await client.process(
                prompt=prompt,
                processing_hint=hint
            )

            print(f"Backend: {result.get('backend', 'unknown')}")
            print(f"Cost: ${result.get('cost', 0):.4f}")
            print(f"Latency: {result.get('latency_ms', 0):.2f}ms")
            print(f"Response: {result.get('response', '')}")

        except Exception as e:
            print(f"Error: {str(e)}")


async def example_cost_optimization():
    """Example 5: Cost-aware processing."""
    print("\n" + "="*80)
    print("Example 5: Cost Optimization")
    print("="*80)

    client = MPCClient(application_id="cost-conscious-app")

    # Batch of simple questions (use cheap processing)
    simple_questions = [
        "What is 2+2?",
        "Is this a greeting: 'Hello there'?",
        "Classify: ERROR",
    ]

    print("\nSimple questions (using rule-based processing):")
    total_cost = 0

    for question in simple_questions:
        result = await client.process(
            prompt=question,
            processing_hint=ProcessingHint.RULE_ENGINE
        )

        cost = result.get('cost', 0)
        total_cost += cost

        print(f"  Q: {question}")
        print(f"  A: {result.get('response', '')}")
        print(f"  Cost: ${cost:.4f}")

    print(f"\nTotal cost for simple questions: ${total_cost:.4f}")

    # Complex question (use LLM)
    complex_question = "Analyze the security implications of this architecture and provide recommendations"

    print(f"\nComplex question (using LLM):")
    print(f"  Q: {complex_question}")

    result = await client.process(
        prompt=complex_question,
        processing_hint=ProcessingHint.AUTO  # Will auto-select based on complexity
    )

    print(f"  Backend: {result.get('backend', 'unknown')}")
    print(f"  Cost: ${result.get('cost', 0):.4f}")
    print(f"  Response: {result.get('response', '')[:150]}...")


async def example_confidence_cascade():
    """Example 6: Confidence cascade (fallback mechanism)."""
    print("\n" + "="*80)
    print("Example 6: Confidence Cascade")
    print("="*80)

    client = MPCClient(application_id="cascade-app")

    # Question that rules might not handle well
    ambiguous_question = "What does this mean: 'The spirit is willing but the flesh is weak'?"

    print(f"\nAmbiguous question: {ambiguous_question}")
    print("Strategy: Try rules first, fallback to LLM if confidence < threshold")

    result = await client.process(
        prompt=ambiguous_question,
        processing_hint=ProcessingHint.HYBRID  # Use hybrid for cascade
    )

    print(f"\nBackend: {result.get('backend', 'unknown')}")
    print(f"Strategy: {result.get('strategy', 'unknown')}")
    print(f"Confidence: {result.get('confidence', 0):.2f}")
    print(f"Response: {result.get('response', '')}")

    if 'rule_result' in result:
        print(f"Rule-based result: {result['rule_result']}")


async def example_authentication_flow():
    """Example 7: Authentication and authorization."""
    print("\n" + "="*80)
    print("Example 7: Authentication & Authorization")
    print("="*80)

    # Create access control system
    access_control = AccessControl(
        jwt_secret="example-secret",
        hmac_secret="example-hmac"
    )

    # Create tokens for different roles
    user_token = access_control.token_manager.create_token(
        client_id="user-123",
        role=Role.USER,
        permissions=[Permission.READ, Permission.EXECUTE]
    )

    service_token = access_control.token_manager.create_token(
        client_id="service-analytics",
        role=Role.SERVICE,
        permissions=[Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.PII_ACCESS]
    )

    # User request (limited permissions)
    print("\n1. User Request (limited permissions)")
    user_client = MPCClient(auth_token=user_token, application_id="user-app")

    try:
        result = await user_client.process(
            prompt="Analyze data",
            sensitivity=SensitivityLevel.INTERNAL
        )
        print(f"  Success: {result.get('response', '')[:50]}...")
    except Exception as e:
        print(f"  Error: {str(e)}")

    # Service request (full permissions)
    print("\n2. Service Request (full permissions)")
    service_client = MPCClient(auth_token=service_token, application_id="service-app")

    try:
        result = await service_client.process(
            prompt="Process sensitive customer data",
            sensitivity=SensitivityLevel.SENSITIVE,
            processing_hint=ProcessingHint.MODEL_PRIVATE
        )
        print(f"  Success: {result.get('response', '')[:50]}...")
    except Exception as e:
        print(f"  Error: {str(e)}")


async def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("AI SIEM - 3-Layer Architecture Examples")
    print("="*80)
    print(f"Time: {datetime.now().isoformat()}")

    examples = [
        ("Basic Usage", example_basic_usage),
        ("PII Handling", example_pii_handling),
        ("Sensitivity Levels", example_sensitivity_levels),
        ("Processing Hints", example_processing_hints),
        ("Cost Optimization", example_cost_optimization),
        ("Confidence Cascade", example_confidence_cascade),
        ("Authentication Flow", example_authentication_flow),
    ]

    for name, example_func in examples:
        try:
            await example_func()
        except Exception as e:
            logger.error(f"Error in example '{name}': {str(e)}", exc_info=True)
            print(f"\n⚠️  Error in example: {str(e)}\n")

    print("\n" + "="*80)
    print("Examples completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
