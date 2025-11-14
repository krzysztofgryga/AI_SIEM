"""
Collection Layer - MPC Server for request routing and orchestration.

This layer receives requests from applications and routes them to appropriate processing backends.
"""
from .server import MPCServer, MPCServerConfig
from .router import IntelligentRouter

__all__ = ['MPCServer', 'MPCServerConfig', 'IntelligentRouter']
