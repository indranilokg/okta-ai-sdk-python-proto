# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0-alpha.1] - 2024-01-XX

### Added
- Initial release of Okta AI SDK for Python
- **Token Exchange**: OAuth 2.0 Token Exchange (RFC 8693) implementation
- **Cross-App Access**: Identity Assertion Authorization Grant (ID-JAG) for secure cross-application access
- **Core SDK**: Main `OktaAISDK` class with unified access to all functionality
- **Type Safety**: Full Pydantic model support with comprehensive type hints
- **Error Handling**: Structured error handling with custom `SDKError` class
- **Token Verification**: Built-in JWT token verification using JWKS
- **Token Validation**: Basic token format validation
- **LangGraph Integration**: Example implementations for LangGraph agents
- **Comprehensive Testing**: Unit tests, integration tests, and mocking support
- **Documentation**: Complete README, API reference, and usage examples

### Features
- 🔄 **Token Exchange**: Exchange tokens for different audiences and scopes
- 🌐 **Cross-App Access**: Secure cross-application access with ID-JAG tokens
- 🛡️ **Security**: Built-in token verification and validation
- 🐍 **Python**: Full Python 3.8+ support with type hints
- 🤖 **AI-Ready**: Designed for LangGraph agents and AI applications
- 📦 **Type Safety**: Full Pydantic model support with validation

### API Components
- `OktaAISDK`: Main SDK class
- `TokenExchangeClient`: Token exchange functionality
- `CrossAppAccessClient`: Cross-app access (ID-JAG) functionality
- `OktaAIConfig`: Configuration management
- `SDKError`: Custom error handling

### Examples
- Basic usage example
- LangGraph agent integration example
- Token exchange workflows
- Cross-app access patterns

### Testing
- Unit tests for all components
- Integration tests for real Okta environments
- Mock-based testing for development
- Coverage reporting and quality gates

### Dependencies
- `requests>=2.28.0`: HTTP client
- `PyJWT>=2.6.0`: JWT handling
- `cryptography>=3.4.8`: Cryptographic operations
- `pydantic>=1.10.0`: Data validation and settings

### Development
- Black code formatting
- isort import sorting
- mypy type checking
- flake8 linting
- pytest testing framework
- Coverage reporting


