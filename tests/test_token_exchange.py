"""
Tests for Token Exchange functionality
"""

import pytest
import json
import base64
from unittest.mock import Mock, patch, MagicMock
from okta_ai_sdk import (
    OktaAISDK,
    TokenExchangeClient,
    TokenExchangeRequest,
    TokenExchangeResponse,
    TokenVerificationOptions,
    TokenVerificationResult,
    SDKError
)


class TestTokenExchangeClient:
    """Test TokenExchangeClient class"""
    
    def test_client_initialization(self, mock_config):
        """Test client initialization"""
        client = TokenExchangeClient(mock_config)
        
        assert client.config == mock_config
        assert client.session is not None
    
    @patch('requests.Session.post')
    def test_exchange_token_success(self, mock_post, mock_config, mock_token_exchange_response):
        """Test successful token exchange"""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = mock_token_exchange_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        client = TokenExchangeClient(mock_config)
        
        request = TokenExchangeRequest(
            subject_token="test_token",
            subject_token_type="urn:ietf:params:oauth:token-type:access_token",
            audience="https://api.example.com",
            scope="read write"
        )
        
        result = client.exchange_token(request)
        
        assert isinstance(result, TokenExchangeResponse)
        assert result.access_token == mock_token_exchange_response["access_token"]
        assert result.issued_token_type == mock_token_exchange_response["issued_token_type"]
        assert result.token_type == mock_token_exchange_response["token_type"]
        assert result.expires_in == mock_token_exchange_response["expires_in"]
        assert result.scope == mock_token_exchange_response["scope"]
        
        # Verify the request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "data" in call_args.kwargs
        assert call_args.kwargs["data"]["grant_type"] == "urn:ietf:params:oauth:grant-type:token-exchange"
        assert call_args.kwargs["data"]["subject_token"] == "test_token"
        assert call_args.kwargs["data"]["audience"] == "https://api.example.com"
    
    @patch('requests.Session.post')
    def test_exchange_token_with_client_secret(self, mock_post, mock_config, mock_token_exchange_response):
        """Test token exchange with client secret"""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = mock_token_exchange_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        client = TokenExchangeClient(mock_config)
        
        request = TokenExchangeRequest(
            subject_token="test_token",
            subject_token_type="urn:ietf:params:oauth:token-type:access_token",
            audience="https://api.example.com"
        )
        
        result = client.exchange_token(request)
        
        # Verify client secret was included
        call_args = mock_post.call_args
        assert call_args.kwargs["data"]["client_secret"] == mock_config.client_secret
    
    @patch('requests.Session.post')
    def test_exchange_token_http_error(self, mock_post, mock_config):
        """Test token exchange with HTTP error"""
        # Setup mock response with error
        mock_response = Mock()
        mock_response.json.return_value = {
            "error": "invalid_request",
            "error_description": "Invalid token"
        }
        mock_response.status_code = 400
        
        # Mock the exception
        import requests
        mock_post.side_effect = requests.exceptions.HTTPError()
        mock_post.side_effect.response = mock_response
        
        client = TokenExchangeClient(mock_config)
        
        request = TokenExchangeRequest(
            subject_token="invalid_token",
            subject_token_type="urn:ietf:params:oauth:token-type:access_token",
            audience="https://api.example.com"
        )
        
        with pytest.raises(SDKError) as exc_info:
            client.exchange_token(request)
        
        assert exc_info.value.code == "TOKEN_EXCHANGE_FAILED"
        assert exc_info.value.status_code == 400
    
    @patch('jwt.decode')
    @patch('jwt.PyJWKClient')
    def test_verify_token_success(self, mock_jwks_client, mock_jwt_decode, mock_config, mock_jwt_payload):
        """Test successful token verification"""
        # Setup mocks
        mock_jwks_client.return_value.get_signing_key_from_jwt.return_value.key = "test_key"
        mock_jwt_decode.return_value = mock_jwt_payload
        
        client = TokenExchangeClient(mock_config)
        
        options = TokenVerificationOptions(
            issuer="https://test.okta.com",
            audience="test_audience"
        )
        
        result = client.verify_token("test_token", options)
        
        assert isinstance(result, TokenVerificationResult)
        assert result.valid is True
        assert result.sub == mock_jwt_payload["sub"]
        assert result.email == mock_jwt_payload["email"]
        assert result.aud == mock_jwt_payload["aud"]
        assert result.iss == mock_jwt_payload["iss"]
        assert result.exp == mock_jwt_payload["exp"]
        assert result.iat == mock_jwt_payload["iat"]
    
    @patch('jwt.decode')
    @patch('jwt.PyJWKClient')
    def test_verify_token_invalid(self, mock_jwks_client, mock_jwt_decode, mock_config):
        """Test token verification with invalid token"""
        # Setup mocks to raise exception
        from jwt.exceptions import InvalidTokenError
        mock_jwt_decode.side_effect = InvalidTokenError("Invalid token")
        
        client = TokenExchangeClient(mock_config)
        
        options = TokenVerificationOptions(
            issuer="https://test.okta.com",
            audience="test_audience"
        )
        
        result = client.verify_token("invalid_token", options)
        
        assert isinstance(result, TokenVerificationResult)
        assert result.valid is False
        assert "Invalid token" in result.error
    
    def test_validate_token_format_valid(self, mock_config):
        """Test token format validation with valid token"""
        # Create a valid JWT token
        header = {"alg": "RS256", "typ": "JWT"}
        payload = {"sub": "test_user", "aud": "test_audience", "exp": 1234567890}
        
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
        
        valid_token = f"{header_b64}.{payload_b64}.signature"
        
        client = TokenExchangeClient(mock_config)
        
        result = client.validate_token_format(valid_token)
        
        assert result is True
    
    def test_validate_token_format_invalid(self, mock_config):
        """Test token format validation with invalid token"""
        client = TokenExchangeClient(mock_config)
        
        # Test various invalid formats
        invalid_tokens = [
            "invalid.token",
            "not.a.jwt.token",
            "single_part",
            "two.parts",
            "too.many.parts.here.extra"
        ]
        
        for token in invalid_tokens:
            result = client.validate_token_format(token)
            assert result is False
    
    def test_validate_token_format_malformed_json(self, mock_config):
        """Test token format validation with malformed JSON"""
        client = TokenExchangeClient(mock_config)
        
        # Create token with malformed JSON
        malformed_token = "invalid_json.payload.signature"
        
        result = client.validate_token_format(malformed_token)
        
        assert result is False


