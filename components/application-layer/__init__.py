"""
Application Layer - Client interface for AI SIEM.

This layer provides client interfaces for applications to interact with the AI SIEM system.
"""
from .client import MPCClient, SimpleMPCClient

__all__ = ['MPCClient', 'SimpleMPCClient']
