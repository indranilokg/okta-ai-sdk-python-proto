"""
Type definitions for Okta AI SDK
"""

from .core import (
    OktaAIConfig,
    SDKError,
)

from .token_exchange import (
    TokenExchangeRequest,
    TokenExchangeResponse,
    TokenVerificationOptions,
    TokenVerificationResult,
)

from .cross_app_access import (
    IdJagTokenRequest,
    IdJagTokenResponse,
    IdJagTokenVerificationOptions,
    IdJagTokenVerificationResult,
    AuthServerTokenRequest,
    AuthServerTokenResponse,
    AuthServerTokenVerificationOptions,
    AuthServerTokenVerificationResult,
)

__all__ = [
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

