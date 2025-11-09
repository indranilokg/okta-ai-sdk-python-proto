# Okta AI SDK for Python

> **⚠️ IMPORTANT NOTICE: This is a sample prototype implementation and is NOT an official Okta product. This SDK is provided for demonstration and experimentation purposes only. Do not use this in production environments. For official Okta SDKs and support, please visit [developer.okta.com](https://developer.okta.com).**

A comprehensive Python SDK for Okta AI applications with support for Token Exchange and Cross-App Access (ID-JAG). Perfect for LangGraph agents and other AI applications that need secure authentication and authorization.

## Features

- 🔄 **Token Exchange**: OAuth 2.0 Token Exchange (RFC 8693) implementation
- 🌐 **Cross-App Access**: Identity Assertion Authorization Grant (ID-JAG) for secure cross-application access
- 🛡️ **Security**: Built-in token verification and validation
- 🐍 **Python**: Full Python 3.8+ support with comprehensive type hints
- 🤖 **AI-Ready**: Designed for LangGraph agents and AI applications
- 📦 **Type Safety**: Full Pydantic model support with validation

## Installation

```bash
pip install okta-ai-sdk-proto
```

### Development Installation

```bash
git clone https://github.com/okta/okta-ai-sdk-python-proto.git
cd okta-ai-sdk-python-proto
pip install -e .
```

## Quick Start

### Basic Setup (Token Exchange)

```python
from okta_ai_sdk import OktaAISDK, OktaAIConfig

# Token Exchange Configuration
config = OktaAIConfig(
    okta_domain="https://your-domain.okta.com",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    authorization_server_id="default"
)

sdk = OktaAISDK(config)
```

### Cross-App Access Setup (ID-JAG with JWT Bearer)

```python
# For Cross-App Access with JWT Bearer Assertion
config = OktaAIConfig(
    okta_domain="https://your-domain.okta.com",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    authorization_server_id="your-auth-server-id",
    principal_id="YOUR_PRINCIPAL_ID",  # Service account ID
    private_jwk={
        "kty": "RSA",
        "kid": "YOUR_KEY_ID",
        "use": "sig",
        "n": "...",  # Base64url encoded modulus
        "e": "AQAB",
        "d": "...",  # Base64url encoded private exponent
        "p": "...",  # Base64url encoded first prime
        "q": "...",  # Base64url encoded second prime
        "dp": "...", # Base64url encoded first factor CRT exponent
        "dq": "...", # Base64url encoded second factor CRT exponent
        "qi": "..."  # Base64url encoded CRT coefficient
    }
)

sdk = OktaAISDK(config)
```

### Token Exchange

```python
from okta_ai_sdk import TokenExchangeRequest

# Exchange an access token for a new token with different audience
result = sdk.token_exchange.exchange_token(
    TokenExchangeRequest(
        subject_token="YOUR_ACCESS_TOKEN",
        subject_token_type="urn:ietf:params:oauth:token-type:access_token",
        audience="https://api.example.com",
        scope="read write"
    )
)

print(f"New token: {result.access_token}")
```

### Cross-App Access (ID-JAG)

#### Complete 4-Step Flow with JWT Bearer Assertion

This example shows the complete ID-JAG flow with JWT bearer assertion for client authentication:

```python
from okta_ai_sdk import AuthServerTokenRequest

# Ensure config has principal_id and private_jwk set
if not sdk.config.principal_id or not sdk.config.private_jwk:
    raise Exception("principal_id and private_jwk required for JWT bearer authentication")

id_jag_audience = f"{sdk.config.okta_domain}/oauth2/{sdk.config.authorization_server_id}"

# STEP 1: Exchange ID token for ID-JAG token
# Uses JWT bearer assertion automatically from config
id_jag_result = sdk.cross_app_access.exchange_id_token(
    id_token="YOUR_ID_TOKEN",
    audience=id_jag_audience,
    scope="mcp:read"
)
print(f"✅ ID-JAG token obtained (expires in {id_jag_result.expires_in}s)")

# STEP 2: Verify ID-JAG token
# Validates signature, audience, issuer, and expiration
verification_result = sdk.cross_app_access.verify_id_jag_token(
    token=id_jag_result.access_token,
    audience=id_jag_audience
)

if verification_result.valid:
    print(f"✅ ID-JAG token verified")
    print(f"   Subject: {verification_result.sub}")
    print(f"   Audience: {verification_result.aud}")
else:
    print(f"❌ ID-JAG verification failed: {verification_result.error}")
    exit(1)

# STEP 3: Exchange ID-JAG token for authorization server token
# Uses JWT bearer assertion with authorization server-specific audience
auth_server_request = AuthServerTokenRequest(
    id_jag_token=id_jag_result.access_token,
    authorization_server_id=sdk.config.authorization_server_id,
    principal_id=sdk.config.principal_id,
    private_jwk=sdk.config.private_jwk
)

auth_server_result = sdk.cross_app_access.exchange_id_jag_for_auth_server_token(
    auth_server_request
)
print(f"✅ Authorization server token obtained (expires in {auth_server_result.expires_in}s)")

# STEP 4: Verify authorization server token
# Token will be used with your resource server
resource_server_audience = "https://your-resource-server.com"  # Your API/resource server

verification_result = sdk.cross_app_access.verify_auth_server_token(
    token=auth_server_result.access_token,
    authorization_server_id=sdk.config.authorization_server_id,
    audience=resource_server_audience
)

if verification_result.valid:
    print(f"✅ Authorization server token verified")
    print(f"   Subject: {verification_result.sub}")
    print(f"   Audience: {verification_result.aud}")
    print(f"   Scope: {verification_result.scope}")
    print(f"\n✅ Token ready to use with resource server!")
else:
    print(f"❌ Token verification failed: {verification_result.error}")
    exit(1)
```

## LangGraph Agent Integration

Here's how to use the SDK with LangGraph agents for secure multi-organization authentication:

```python
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from okta_ai_sdk import (
    OktaAISDK, OktaAIConfig, TokenExchangeRequest,
    AuthServerTokenRequest
)

@dataclass
class AgentState:
    user_id: str
    access_token: str
    id_token: str
    messages: List[Dict[str, Any]]
    exchanged_tokens: Dict[str, str] = field(default_factory=dict)
    id_jag_token: Optional[str] = None
    auth_server_token: Optional[str] = None

class OktaSecureAgent:
    def __init__(self, 
                 token_exchange_config: OktaAIConfig,
                 cross_app_config: Optional[OktaAIConfig] = None):
        self.sdk = OktaAISDK(token_exchange_config)
        self.cross_app_sdk = OktaAISDK(cross_app_config) if cross_app_config else None
    
    def authenticate_user(self, state: AgentState) -> AgentState:
        """Authenticate user and validate tokens"""
        verification_result = self.sdk.token_exchange.verify_token(
            token=state.access_token,
            options={
                "issuer": self.sdk.config.okta_domain,
                "audience": "api://default"
            }
        )
        
        if verification_result.valid:
            print(f"✅ User authenticated: {verification_result.sub}")
            return state
        
        raise Exception(f"❌ Authentication failed: {verification_result.error}")
    
    def exchange_token_for_app(self, state: AgentState, app_audience: str) -> AgentState:
        """Exchange token for specific application access (Token Exchange)"""
        result = self.sdk.token_exchange.exchange_token(
            TokenExchangeRequest(
                subject_token=state.access_token,
                subject_token_type="urn:ietf:params:oauth:token-type:access_token",
                audience=app_audience,
                scope="read write"
            )
        )
        
        state.exchanged_tokens[app_audience] = result.access_token
        return state
    
    def exchange_for_cross_app_access(self, state: AgentState) -> AgentState:
        """Exchange ID token for cross-app access (ID-JAG) - 4 steps"""
        if not self.cross_app_sdk:
            raise Exception("Cross-app access SDK not configured")
        
        id_jag_audience = f"{self.cross_app_sdk.config.okta_domain}/oauth2/{self.cross_app_sdk.config.authorization_server_id}"
        
        # STEP 1: Exchange ID token for ID-JAG token
        id_jag_result = self.cross_app_sdk.cross_app_access.exchange_id_token(
            id_token=state.id_token,
            audience=id_jag_audience,
            scope="mcp:read"
        )
        state.id_jag_token = id_jag_result.access_token
        print(f"✅ STEP 1: ID-JAG token obtained")
        
        # STEP 2: Verify ID-JAG token
        verification_result = self.cross_app_sdk.cross_app_access.verify_id_jag_token(
            token=state.id_jag_token,
            audience=id_jag_audience
        )
        
        if not verification_result.valid:
            raise Exception(f"STEP 2: ID-JAG verification failed: {verification_result.error}")
        
        print(f"✅ STEP 2: ID-JAG token verified for: {verification_result.sub}")
        
        # STEP 3: Exchange ID-JAG for authorization server token
        auth_server_request = AuthServerTokenRequest(
            id_jag_token=state.id_jag_token,
            authorization_server_id=self.cross_app_sdk.config.authorization_server_id,
            principal_id=self.cross_app_sdk.config.principal_id,
            private_jwk=self.cross_app_sdk.config.private_jwk
        )
        
        auth_server_result = self.cross_app_sdk.cross_app_access.exchange_id_jag_for_auth_server_token(
            auth_server_request
        )
        state.auth_server_token = auth_server_result.access_token
        print(f"✅ STEP 3: Authorization server token obtained")
        
        # STEP 4: Verify authorization server token
        resource_server_audience = "https://your-resource-server.com"  # Your resource server
        verification_result = self.cross_app_sdk.cross_app_access.verify_auth_server_token(
            token=state.auth_server_token,
            authorization_server_id=self.cross_app_sdk.config.authorization_server_id,
            audience=resource_server_audience
        )
        
        if verification_result.valid:
            print(f"✅ STEP 4: Authorization server token verified")
            return state
        
        raise Exception(f"❌ STEP 4: Token verification failed: {verification_result.error}")
```

## API Reference

### Core SDK

#### `OktaAISDK`

Main SDK class providing access to all functionality.

```python
sdk = OktaAISDK(config)
```

**Methods:**
- `get_config()`: Get current configuration
- `update_config(updates)`: Update configuration

### Token Exchange

#### `TokenExchangeClient`

Implements OAuth 2.0 Token Exchange (RFC 8693).

**Methods:**
- `exchange_token(request)`: Exchange a token for a new token
- `verify_token(token, options)`: Verify a token using JWKS
- `validate_token_format(token)`: Basic token format validation

### Cross-App Access

#### `CrossAppAccessClient`

Implements Identity Assertion Authorization Grant (ID-JAG) for secure cross-application access with a clean 4-step token exchange flow. No backward compatibility bloat - just the essential methods you need.

**Methods (4 Core Steps):**

**STEP 1: ID-JAG Token Exchange**
- `exchange_id_token(id_token, audience, scope=None)`: Exchange ID token for ID-JAG token
  - Uses JWT bearer assertion or client credentials from SDK config
  - Returns: `IdJagTokenResponse`

**STEP 2: ID-JAG Token Verification**
- `verify_id_jag_token(token, audience)`: Verify ID-JAG token and extract claims
  - Validates signature, audience, issuer, and expiration
  - Returns: `IdJagTokenVerificationResult`

**STEP 3: Authorization Server Token Exchange**
- `exchange_id_jag_for_auth_server_token(request)`: Exchange ID-JAG for auth server token
  - Requires: `AuthServerTokenRequest` with `id_jag_token`, `authorization_server_id`, `principal_id`, `private_jwk`
  - Uses JWT bearer assertion with auth server-specific audience
  - Returns: `AuthServerTokenResponse`

**STEP 4: Authorization Server Token Verification**
- `verify_auth_server_token(token, authorization_server_id, audience)`: Verify auth server token
  - Validates signature, audience, issuer, and expiration
  - Extracts scope claims from token
  - Returns: `AuthServerTokenVerificationResult`

## Configuration

### Environment Variables

You can use environment variables for configuration:

```bash
export OKTA_DOMAIN="https://your-domain.okta.com"
export OKTA_CLIENT_ID="your-client-id"
export OKTA_CLIENT_SECRET="your-client-secret"
```

```python
import os
from okta_ai_sdk import OktaAIConfig

config = OktaAIConfig(
    okta_domain=os.getenv("OKTA_DOMAIN"),
    client_id=os.getenv("OKTA_CLIENT_ID"),
    client_secret=os.getenv("OKTA_CLIENT_SECRET")
)
```

### Configuration Options

**Token Exchange Configuration:**

```python
config = OktaAIConfig(
    okta_domain="https://your-domain.okta.com",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    authorization_server_id="default"
)
```

**Cross-App Access with JWT Bearer:**

```python
config = OktaAIConfig(
    okta_domain="https://your-domain.okta.com",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    authorization_server_id="your-auth-server-id",
    principal_id="YOUR_SERVICE_ACCOUNT_ID",
    private_jwk={  # RSA private key in JWK format
        "kty": "RSA",
        "kid": "your-key-id",
        "use": "sig",
        "n": "...",   # modulus
        "e": "AQAB",  # public exponent
        "d": "...",   # private exponent
        "p": "...", "q": "...",  # prime factors
        "dp": "...", "dq": "...", "qi": "..."  # CRT parameters
    }
)
```

**Configuration Parameters:**

- `okta_domain` (str, required): Okta organization domain
- `client_id` (str, required): OAuth 2.0 client ID
- `client_secret` (str, optional): Client secret for authentication
- `authorization_server_id` (str, optional): Authorization server ID (default: 'default')
- `principal_id` (str, optional): Service account ID for JWT bearer assertion
- `private_jwk` (dict, optional): Private RSA key in JWK format (for JWT bearer authentication)
- `timeout` (int, optional): Request timeout in milliseconds (default: 30000)
- `retry_attempts` (int, optional): Number of retry attempts (default: 3)

## Error Handling

The SDK provides comprehensive error handling with structured error objects:

```python
from okta_ai_sdk import SDKError

try:
    result = sdk.token_exchange.exchange_token(request)
except SDKError as e:
    print(f"Error code: {e.code}")
    print(f"Error message: {e.message}")
    print(f"Status code: {e.status_code}")
    print(f"Details: {e.details}")
```

### Error Codes

| Code | Description |
|------|-------------|
| `TOKEN_EXCHANGE_FAILED` | Token exchange request failed |
| `TOKEN_EXCHANGE_ERROR` | General token exchange error |
| `ID_JAG_TOKEN_EXCHANGE_FAILED` | ID-JAG token exchange failed |
| `ID_JAG_TOKEN_EXCHANGE_ERROR` | General ID-JAG token exchange error |
| `MISSING_CLIENT_SECRET` | Client secret required but not provided |
| `INVALID_TOKEN_FORMAT` | Token format validation failed |
| `TOKEN_VERIFICATION_FAILED` | Token verification failed |

## Examples

See the `examples/` directory for complete working examples:

- **Basic Usage**: `examples/basic_usage.py`
- **LangGraph Agent**: `examples/langraph_agent_example.py`

## Development

### Setup Development Environment

```bash
git clone https://github.com/okta/okta-ai-sdk-proto.git
cd okta-ai-sdk-proto
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=okta_ai_sdk --cov-report=html

# Run specific test file
pytest tests/test_token_exchange.py
```

### Code Quality

```bash
# Format code
black src/ tests/ examples/

# Sort imports
isort src/ tests/ examples/

# Type checking
mypy src/

# Linting
flake8 src/ tests/ examples/
```

## Requirements

- Python 3.8+
- Okta Developer Account
- OAuth 2.0 application with Token Exchange and ID-JAG enabled

## Dependencies

- `requests>=2.28.0` - HTTP client
- `PyJWT>=2.6.0` - JWT handling
- `cryptography>=3.4.8` - Cryptographic operations
- `pydantic>=1.10.0` - Data validation and settings

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

- 📖 [Documentation](https://github.com/okta/okta-ai-sdk-proto#readme)
- 🐛 [Issue Tracker](https://github.com/okta/okta-ai-sdk-proto/issues)
- 💬 [Discussions](https://github.com/okta/okta-ai-sdk-proto/discussions)

## Changelog

### 1.0.0-alpha.6

- **README Improvements**: Complete configuration documentation
- Fixed repository folder name references (okta-ai-sdk-python-proto)
- Added comprehensive setup examples for Token Exchange and ID-JAG
- Documented all configuration parameters with examples
- Simplified JWK documentation (removed verbose CRT parameter explanations)
- Enhanced Cross-App Access example with validation and error handling
- Complete 4-step ID-JAG flow documentation with JWT bearer details

### 1.0.0-alpha.5

- **README Consistency**: Fixed all code examples to use new simplified 4-method API
- Removed obsolete "Convenience Method" section
- Fixed imports (removed non-existent `AuthServerTokenVerificationOptions`)
- Updated all method calls to match simplified signatures
- Verified consistency across client.py, README.md, and test_package.py
- Test README updated to document v1.0.0-alpha.4+ features

### 1.0.0-alpha.4

- **SIMPLIFIED API**: Removed all intermediate and convenience methods
- **4 Core Methods Only**: `exchange_id_token()`, `verify_id_jag_token()`, `exchange_id_jag_for_auth_server_token()`, `verify_auth_server_token()`
- Clean, focused API with no backward compatibility baggage
- Updated LangGraph Agent Integration with simplified method signatures
- Removed utility methods and duplicate implementations
- All documentation updated to reflect the streamlined API

### 1.0.0-alpha.3

- Updated documentation with complete examples
- Enhanced LangGraph Agent Integration with 4-step cross-app access flow
- Comprehensive API reference for all methods
- Added step-by-step examples for token exchange and cross-app access
- Improved README with multi-organization setup guide

### 1.0.0-alpha.2

- Enhanced Cross-App Access with 4-step token exchange flow
- Added `exchange_id_jag_for_auth_server_token()` method for authorization server token exchange
- Added `verify_auth_server_token()` method for authorization server token verification
- JWT bearer assertion with authorization server-specific audience
- Full support for multi-organization token flows

### 1.0.0-alpha.1

- Initial release
- Token Exchange support (RFC 8693)
- Cross-App Access (ID-JAG) basic support
- LangGraph agent integration examples
- Comprehensive error handling
- Full type safety with Pydantic

