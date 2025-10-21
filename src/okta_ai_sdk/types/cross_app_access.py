"""
Cross-App Access (ID-JAG) type definitions
"""

from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class IdJagTokenRequest(BaseModel):
    """ID-JAG Token Request"""
    subject_token: str = Field(..., description="The Okta ID token to exchange")
    audience: str = Field(..., description="Target audience (e.g., 'http://localhost:5001')")
    client_id: str = Field(..., description="Okta client ID")
    client_secret: str = Field(..., description="Okta client secret")


class IdJagTokenResponse(BaseModel):
    """ID-JAG Token Response"""
    access_token: str = Field(..., description="The ID-JAG token")
    issued_token_type: str = Field(..., description="Should be 'urn:ietf:params:oauth:token-type:id-jag'")
    token_type: str = Field(..., description="Should be 'Bearer'")
    expires_in: Optional[int] = Field(None, description="Token expiration in seconds")
    scope: Optional[str] = Field(None, description="Token scope")


class IdJagTokenVerificationOptions(BaseModel):
    """ID-JAG Token Verification Options"""
    issuer: str = Field(..., description="Expected issuer (e.g., 'https://your-domain.okta.com')")
    audience: str = Field(..., description="Expected audience (e.g., 'http://localhost:5001')")
    jwks_uri: Optional[str] = Field(None, description="Optional JWKS URI, defaults to issuer + /oauth2/v1/keys")


class IdJagTokenVerificationResult(BaseModel):
    """ID-JAG Token Verification Result"""
    valid: bool = Field(..., description="Whether the token is valid")
    payload: Optional[Dict[str, Any]] = Field(None, description="Decoded token payload")
    sub: Optional[str] = Field(None, description="Token subject")
    email: Optional[str] = Field(None, description="User email from token")
    aud: Optional[str] = Field(None, description="Token audience")
    iss: Optional[str] = Field(None, description="Token issuer")
    exp: Optional[int] = Field(None, description="Token expiration timestamp")
    error: Optional[str] = Field(None, description="Error message if verification failed")

