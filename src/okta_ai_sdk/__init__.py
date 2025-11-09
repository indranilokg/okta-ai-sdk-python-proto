"""
Okta AI SDK for Python

A comprehensive Python SDK for Okta AI applications with support for 
Token Exchange and Cross-App Access (ID-JAG).
"""

from .core.sdk import OktaAISDK
from .token_exchange.client import TokenExchangeClient
from .cross_app_access.client import CrossAppAccessClient

# Type exports
from .types import (
    # Core types
    OktaAIConfig,
    SDKError,
    
    # Token Exchange types
    TokenExchangeRequest,
    TokenExchangeResponse,
    TokenVerificationOptions,
    TokenVerificationResult,
    
    # Cross-App Access (ID-JAG) types
    IdJagTokenRequest,
    IdJagTokenResponse,
    IdJagTokenVerificationOptions,
    IdJagTokenVerificationResult,
    AuthServerTokenRequest,
    AuthServerTokenResponse,
    AuthServerTokenVerificationOptions,
    AuthServerTokenVerificationResult,
)

__version__ = "1.0.0-alpha.1"
__author__ = "Okta Inc."

__all__ = [
    # Main SDK class
    "OktaAISDK",
    
    # Client classes
    "TokenExchangeClient",
    "CrossAppAccessClient",
    
    # Core types
    "OktaAIConfig",
    "SDKError",
    
    # Token Exchange types
    "TokenExchangeRequest",
    "TokenExchangeResponse",
    "TokenVerificationOptions",
    "TokenVerificationResult",
    
    # Cross-App Access types
    "IdJagTokenRequest",
    "IdJagTokenResponse",
    "IdJagTokenVerificationOptions",
    "IdJagTokenVerificationResult",
    "AuthServerTokenRequest",
    "AuthServerTokenResponse",
    "AuthServerTokenVerificationOptions",
    "AuthServerTokenVerificationResult",
]

