# Contributing to AI Agent Security Monitoring Platform

Thank you for your interest in contributing! 🎉

## Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/AI_SIEM.git
   cd AI_SIEM
   ```
3. **Set up development environment**
   ```bash
   cd poc
   make setup
   ```

## Development Workflow

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes
- Write clean, readable code
- Follow existing code style
- Add tests if applicable
- Update documentation

### 3. Test Your Changes
```bash
# Run examples
make test

# Test with different providers
python test_all_llms.py

# Check the CLI
make cli
```

### 4. Commit Changes
```bash
git add .
git commit -m "feat: add amazing feature"
# or
git commit -m "fix: resolve issue with X"
```

**Commit Message Format:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

### 5. Push and Create PR
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Style

### Python
- Follow PEP 8
- Use type hints where possible
- Write docstrings for public functions
- Keep functions focused and small

Example:
```python
from typing import Optional, Dict, Any

async def process_event(event: AIEvent, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Process an AI event with optional configuration.

    Args:
        event: The event to process
        config: Optional configuration dictionary

    Returns:
        Processed event data
    """
    # Implementation
    pass
```

### Documentation
- Update README.md if needed
- Add docstrings to new functions/classes
- Include examples for new features
- Keep docs clear and concise

## Areas for Contribution

### 🔥 High Priority
- [ ] Web dashboard (Streamlit/Gradio)
- [ ] Slack integration for alerts
- [ ] ML-based anomaly detection
- [ ] Elasticsearch storage backend
- [ ] Kafka event streaming

### 🎯 Medium Priority
- [ ] Additional LLM providers (Cohere, HuggingFace)
- [ ] Custom alert rules
- [ ] Export to CSV/JSON
- [ ] Rate limiting per user
- [ ] Multi-tenancy support

### 💡 Nice to Have
- [ ] Grafana dashboards
- [ ] Kubernetes Helm charts
- [ ] Prometheus exporter
- [ ] Auto-remediation actions
- [ ] GDPR compliance checks

### 🐛 Bug Fixes
Always welcome! Please include:
- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Your fix

## Adding New LLM Provider

Template for adding support for a new provider:

```python
class NewProviderCollector(BaseCollector):
    """Collector for NewProvider LLM."""

    def __init__(self, base_url: str, event_handler=None, user_id: Optional[str] = None):
        super().__init__(event_handler)
        self.base_url = base_url
        self.user_id = user_id
        self.session_id = str(uuid.uuid4())
        self.client = httpx.AsyncClient()

    async def generate(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate completion with monitoring."""
        event_id = str(uuid.uuid4())
        start_time = time.time()

        try:
            # Call provider API
            response = await self.client.post(...)

            # Calculate metrics
            latency_ms = (time.time() - start_time) * 1000

            # Create event
            event = AIEvent(
                id=event_id,
                provider=Provider.CUSTOM,
                model=model,
                prompt=prompt,
                response=...,
                latency_ms=latency_ms,
                tokens=...,
                cost_usd=...,
                success=True,
                metadata={'provider': 'newprovider'}
            )

            # Emit event
            await self.emit_event(event)

            return response

        except Exception as e:
            # Error handling
            await self.emit_event(error_event)
            raise
```

## Testing

### Manual Testing
```bash
# Test your collector
python -c "
import asyncio
from your_collector import YourCollector

async def test():
    collector = YourCollector(...)
    result = await collector.generate(...)
    print(result)

asyncio.run(test())
"
```

### Integration Testing
```bash
# Run full example
make test

# Check dashboard
make cli
make stats
```

## Documentation Guidelines

### README Updates
When adding features, update:
- Feature list
- Usage examples
- Configuration section
- Roadmap

### Code Documentation
```python
def my_function(param1: str, param2: int) -> Dict:
    """
    Brief description of what the function does.

    Longer description if needed, explaining the logic,
    edge cases, or important details.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is invalid
        RuntimeError: When something goes wrong

    Example:
        >>> result = my_function("test", 42)
        >>> print(result)
        {'status': 'success'}
    """
    pass
```

## Pull Request Checklist

Before submitting your PR, make sure:

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] PR description explains the changes
- [ ] No sensitive data in commits
- [ ] Branch is up to date with main

## Questions?

- Open an issue for discussion
- Check existing issues/PRs first
- Be respectful and constructive

## Code of Conduct

- Be kind and respectful
- Welcome newcomers
- Focus on constructive feedback
- No harassment or discrimination
- Help each other learn

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing!** 🙏

Every contribution, no matter how small, makes this project better.
