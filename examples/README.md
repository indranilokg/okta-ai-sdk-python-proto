# Okta AI SDK Examples

This directory contains example usage of the Okta AI SDK for Python.

## Examples

### 1. Basic Usage (`basic_usage.py`)

Demonstrates basic functionality of the SDK:
- Token exchange
- Cross-app access (ID-JAG)
- Token format validation

**Usage:**
```bash
python examples/basic_usage.py
```

### 2. LangGraph Agent Example (`langraph_agent_example.py`)

Shows how to integrate the SDK with LangGraph agents for:
- User authentication
- Token exchange for different applications
- Cross-app access management
- Secure token handling in agent workflows

**Usage:**
```bash
python examples/langraph_agent_example.py
```

## Configuration

Before running the examples, you need to configure your Okta settings:

1. **Replace placeholder values** in the example files:
   - `https://your-domain.okta.com` → Your actual Okta domain
   - `YOUR_CLIENT_ID` → Your Okta client ID
   - `YOUR_CLIENT_SECRET` → Your Okta client secret
   - `YOUR_ACCESS_TOKEN` → A valid access token
   - `YOUR_ID_TOKEN` → A valid ID token

2. **Set up your Okta application** with the following features:
   - Token Exchange grant type
   - Cross-app access (ID-JAG) support
   - Appropriate scopes and audiences

## Environment Variables

You can also use environment variables for configuration:

```bash
export OKTA_DOMAIN="https://your-domain.okta.com"
export OKTA_CLIENT_ID="your-client-id"
export OKTA_CLIENT_SECRET="your-client-secret"
```

Then modify the examples to use:
```python
config = OktaAIConfig(
    okta_domain=os.getenv("OKTA_DOMAIN"),
    client_id=os.getenv("OKTA_CLIENT_ID"),
    client_secret=os.getenv("OKTA_CLIENT_SECRET")
)
```

## Prerequisites

1. **Python 3.8+**
2. **Okta Developer Account** with:
   - Custom authorization server
   - OAuth 2.0 application configured
   - Token Exchange and ID-JAG enabled

3. **Dependencies** (install with `pip install -r requirements.txt`):
   - requests
   - PyJWT
   - cryptography
   - pydantic

## Running Examples

1. **Install the SDK** (from the project root):
   ```bash
   pip install -e .
   ```

2. **Run an example**:
   ```bash
   python examples/basic_usage.py
   ```

## Error Handling

The examples include comprehensive error handling for:
- Invalid tokens
- Network errors
- Configuration issues
- Token exchange failures

Check the console output for detailed error messages and troubleshooting information.


