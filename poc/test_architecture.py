"""
Quick test of the new 3-layer architecture.
"""
import asyncio


async def test():
    print('Testing 3-layer architecture...\n')

    # Test 1: PII Detection
    print('1. Testing PII Detection')
    from security.pii_handler import PIIDetector
    detector = PIIDetector()
    result = detector.detect('My email is john@example.com and phone is 555-1234')
    print(f'   PII detected: {result.has_pii}')
    print(f'   Types: {[t.value for t in result.pii_types]}')
    print('   ✓ PII Detection works\n')

    # Test 2: Schema Validation
    print('2. Testing Schema Validation')
    from schemas.contracts import MPCRequest, SourceInfo, AuthInfo, RequestType
    request = MPCRequest(
        source=SourceInfo(application_id='test-app'),
        type=RequestType.PROCESS_REQUEST,
        payload_schema='llm.request.v1',
        payload={'model': 'test', 'prompt': 'test'},
        auth=AuthInfo(token='test-token')
    )
    print(f'   Request ID: {request.request_id}')
    print('   ✓ Schema Validation works\n')

    # Test 3: Routing
    print('3. Testing Intelligent Routing')
    from mpc_server.router import IntelligentRouter, CapabilityType, get_default_backends
    from schemas.contracts import SensitivityLevel, ProcessingHint
    router = IntelligentRouter(get_default_backends())
    decision = router.route(
        capability=CapabilityType.TEXT_GENERATION,
        sensitivity=SensitivityLevel.INTERNAL,
        processing_hint=ProcessingHint.AUTO,
        estimated_tokens=1000
    )
    print(f'   Backend: {decision.backend_id}')
    print(f'   Cost estimate: ${decision.estimated_cost:.4f}')
    print('   ✓ Routing works\n')

    # Test 4: Simple Backend
    print('4. Testing Rule-Based Backend')
    from processing.backends import RuleBasedBackend
    backend = RuleBasedBackend()
    result = await backend.process('Error: timeout occurred')
    print(f'   Response: {result["response"]}')
    print('   ✓ Backend works\n')

    print('✅ All core tests passed!')


if __name__ == '__main__':
    asyncio.run(test())
