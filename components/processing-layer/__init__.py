"""
Processing Layer - Backend processors for AI requests.

This layer contains different processing backends (rule engines, LLM models, etc.).
"""
from .backends import (
    ProcessingBackend,
    BackendRegistry,
    get_backend_registry,
    initialize_default_backends
)

__all__ = [
    'ProcessingBackend',
    'BackendRegistry',
    'get_backend_registry',
    'initialize_default_backends'
]
