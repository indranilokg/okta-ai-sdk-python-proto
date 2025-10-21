"""
Tests for Cross-App Access functionality
"""

import pytest
import json
import base64
from unittest.mock import Mock, patch
from okta_ai_sdk import (
    CrossAppAccessClient,
    IdJagTokenRequest,
    IdJagTokenResponse,
    IdJagTokenVerificationOptions,
    IdJagTokenVerificationResult,
    SDKError
)


class TestCrossAppAccessClient:
    """Test CrossAppAccessClient class"""
    
    def test_client_initialization(self, mock_config):
        """Test client initialization"""
        client = CrossAppAccessClient(mock_config)
        
        assert client.config == mock_config
        assert client.session is not None
    
    @patch('requests.Session.post')
    def test_exchange_id_token_for_id_jag_success(self, mock_post, mock_config, mock_id_jag_response):
        """Test successful ID-JAG token exchange"""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = mock_id_jag_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        client = CrossAppAccessClient(mock_config)
        
        request = IdJagTokenRequest(
            subject_token="test_id_token",
            audience="http://localhost:5001",
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        
        result = client.exchange_id_token_for_id_jag(request)
        
        assert isinstance(result, IdJagTokenResponse)
        assert result.access_token == mock_id_jag_response["access_token"]
        assert result.issued_token_type == mock_id_jag_response["issued_token_type"]
        assert result.token_type == mock_id_jag_response["token_type"]
        assert result.expires_in == mock_id_jag_response["expires_in"]
        assert result.scope == mock_id_jag_response["scope"]
        
        # Verify the request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "data" in call_args.kwargs
        assert call_args.kwargs["data"]["grant_type"] == "urn:ietf:params:oauth:grant-type:token-exchange"
        assert call_args.kwargs["data"]["requested_token_type"] == "urn:ietf:params:oauth:token-type:id-jag"
        assert call_args.kwargs["data"]["subject_token"] == "test_id_token"
        assert call_args.kwargs["data"]["audience"] == "http://localhost:5001"
    
    @patch('requests.Session.post')
    def test_exchange_id_token_for_id_jag_http_error(self, mock_post, mock_config):
        """Test ID-JAG token exchange with HTTP error"""
        # Setup mock response with error
        mock_response = Mock()
        mock_response.json.return_value = {
            "error": "invalid_request",
            "error_description": "Invalid ID token"
        }
        mock_response.status_code = 400
        
        # Mock the exception
        import requests
        mock_post.side_effect = requests.exceptions.HTTPError()
        mock_post.side_effect.response = mock_response
        
        client = CrossAppAccessClient(mock_config)
        
        request = IdJagTokenRequest(
            subject_token="invalid_id_token",
            audience="http://localhost:5001",
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        
        with pytest.raises(SDKError) as exc_info:
            client.exchange_id_token_for_id_jag(request)
        
        assert exc_info.value.code == "ID_JAG_TOKEN_EXCHANGE_FAILED"
        assert exc_info.value.status_code == 400
    
    def test_exchange_id_token_convenience_method(self, mock_config):
        """Test convenience method for ID token exchange"""
        client = CrossAppAccessClient(mock_config)
        
        with patch.object(client, 'exchange_id_token_for_id_jag') as mock_exchange:
            mock_exchange.return_value = IdJagTokenResponse(
                access_token="test_token",
                issued_token_type="urn:ietf:params:oauth:token-type:id-jag",
                token_type="Bearer",
                expires_in=3600
            )
            
            result = client.exchange_id_token("test_id_token", "http://localhost:5001")
            
            # Verify the convenience method was called with correct parameters
            mock_exchange.assert_called_once()
            call_args = mock_exchange.call_args[0][0]  # First positional argument
            assert isinstance(call_args, IdJagTokenRequest)
            assert call_args.subject_token == "test_id_token"
            assert call_args.audience == "http://localhost:5001"
            assert call_args.client_id == mock_config.client_id
            assert call_args.client_secret == mock_config.client_secret
    
    def test_exchange_id_token_missing_client_secret(self):
        """Test ID token exchange without client secret"""
        config = mock_config = Mock()
        config.client_id = "test_client_id"
        config.client_secret = None  # No client secret
        
        client = CrossAppAccessClient(config)
        
        with pytest.raises(SDKError) as exc_info:
            client.exchange_id_token("test_id_token", "http://localhost:5001")
        
        assert exc_info.value.code == "MISSING_CLIENT_SECRET"
    
    @patch('jwt.decode')
    @patch('jwt.PyJWKClient')
    def test_verify_id_jag_token_success(self, mock_jwks_client, mock_jwt_decode, mock_config, mock_jwt_payload):
        """Test successful ID-JAG token verification"""
        # Setup mocks
        mock_jwks_client.return_value.get_signing_key_from_jwt.return_value.key = "test_key"
        mock_jwt_decode.return_value = mock_jwt_payload
        
        client = CrossAppAccessClient(mock_config)
        
        options = IdJagTokenVerificationOptions(
            issuer="https://test.okta.com",
            audience="http://localhost:5001"
        )
        
        result = client.verify_id_jag_token("test_token", options)
        
        assert isinstance(result, IdJagTokenVerificationResult)
        assert result.valid is True
        assert result.sub == mock_jwt_payload["sub"]
        assert result.email == mock_jwt_payload["email"]
        assert result.aud == mock_jwt_payload["aud"]
        assert result.iss == mock_jwt_payload["iss"]
        assert result.exp == mock_jwt_payload["exp"]
    
    @patch('jwt.decode')
    @patch('jwt.PyJWKClient')
    def test_verify_id_jag_token_invalid(self, mock_jwks_client, mock_jwt_decode, mock_config):
        """Test ID-JAG token verification with invalid token"""
        # Setup mocks to raise exception
        from jwt.exceptions import InvalidTokenError
        mock_jwt_decode.side_effect = InvalidTokenError("Invalid token")
        
        client = CrossAppAccessClient(mock_config)
        
        options = IdJagTokenVerificationOptions(
            issuer="https://test.okta.com",
            audience="http://localhost:5001"
        )
        
        result = client.verify_id_jag_token("invalid_token", options)
        
        assert isinstance(result, IdJagTokenVerificationResult)
        assert result.valid is False
        assert "Invalid token" in result.error
    
    def test_verify_id_jag_token_with_config(self, mock_config):
        """Test ID-JAG token verification with SDK config"""
        client = CrossAppAccessClient(mock_config)
        
        with patch.object(client, 'verify_id_jag_token') as mock_verify:
            mock_verify.return_value = IdJagTokenVerificationResult(valid=True)
            
            result = client.verify_id_jag_token_with_config("test_token", "http://localhost:5001")
            
            # Verify the method was called with correct options
            mock_verify.assert_called_once()
            call_args = mock_verify.call_args
            assert call_args[0][0] == "test_token"  # token
            options = call_args[0][1]  # options
            assert isinstance(options, IdJagTokenVerificationOptions)
            assert options.issuer == mock_config.okta_domain
            assert options.audience == "http://localhost:5001"
    
    def test_validate_id_jag_token_format_valid(self, mock_config):
        """Test ID-JAG token format validation with valid token"""
        # Create a valid JWT token
        header = {"alg": "RS256", "typ": "JWT"}
        payload = {"sub": "test_user", "aud": "test_audience", "exp": 1234567890}
        
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
        
        valid_token = f"{header_b64}.{payload_b64}.signature"
        
        client = CrossAppAccessClient(mock_config)
        
        result = client.validate_id_jag_token_format(valid_token)
        
        assert result is True
    
    def test_validate_id_jag_token_format_invalid(self, mock_config):
        """Test ID-JAG token format validation with invalid token"""
        client = CrossAppAccessClient(mock_config)
        
        # Test various invalid formats
        invalid_tokens = [
            "invalid.token",
            "not.a.jwt.token",
            "single_part",
            "two.parts",
            "too.many.parts.here.extra"
        ]
        
        for token in invalid_tokens:
            result = client.validate_id_jag_token_format(token)
            assert result is False
    
    def test_validate_id_jag_token_format_malformed_json(self, mock_config):
        """Test ID-JAG token format validation with malformed JSON"""
        client = CrossAppAccessClient(mock_config)
        
        # Create token with malformed JSON
        malformed_token = "invalid_json.payload.signature"
        
        result = client.validate_id_jag_token_format(malformed_token)
        
        assert result is False


