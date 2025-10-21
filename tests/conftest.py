"""
Pytest configuration and fixtures
"""

import pytest
from unittest.mock import Mock, patch
from okta_ai_sdk import OktaAIConfig


@pytest.fixture
def mock_config():
    """Mock Okta AI configuration"""
    return OktaAIConfig(
        okta_domain="https://test.okta.com",
        client_id="test_client_id",
        client_secret="test_client_secret",
        authorization_server_id="default",
        timeout=30000,
        retry_attempts=3
    )


@pytest.fixture
def mock_token_exchange_response():
    """Mock token exchange response"""
    return {
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test.token",
        "issued_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "read write"
    }


@pytest.fixture
def mock_id_jag_response():
    """Mock ID-JAG token response"""
    return {
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.id.jag.token",
        "issued_token_type": "urn:ietf:params:oauth:token-type:id-jag",
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "openid"
    }


@pytest.fixture
def mock_jwt_payload():
    """Mock JWT payload"""
    return {
        "sub": "test_user_123",
        "email": "test@example.com",
        "aud": "test_audience",
        "iss": "https://test.okta.com",
        "exp": 1234567890,
        "iat": 1234567890
    }


@pytest.fixture
def mock_requests_session():
    """Mock requests session"""
    with patch('requests.Session') as mock_session:
        yield mock_session.return_value


