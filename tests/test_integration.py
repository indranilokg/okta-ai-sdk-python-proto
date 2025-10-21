"""
Integration tests for Okta AI SDK

These tests require actual Okta configuration and are marked as integration tests.
Run with: pytest -m integration
"""

import pytest
import os
from okta_ai_sdk import (
    OktaAISDK,
    OktaAIConfig,
    TokenExchangeRequest,
    IdJagTokenRequest,
    SDKError
)


@pytest.mark.integration
class TestIntegration:
    """Integration tests requiring real Okta configuration"""
    
    @pytest.fixture(scope="class")
    def integration_config(self):
        """Get integration test configuration from environment"""
        config = OktaAIConfig(
            okta_domain=os.getenv("OKTA_DOMAIN"),
            client_id=os.getenv("OKTA_CLIENT_ID"),
            client_secret=os.getenv("OKTA_CLIENT_SECRET"),
            authorization_server_id=os.getenv("OKTA_AUTH_SERVER_ID", "default")
        )
        
        # Validate required environment variables
        if not config.okta_domain or not config.client_id:
            pytest.skip("Integration tests require OKTA_DOMAIN and OKTA_CLIENT_ID environment variables")
        
        return config
    
    @pytest.fixture(scope="class")
    def integration_sdk(self, integration_config):
        """Create SDK instance for integration tests"""
        return OktaAISDK(integration_config)
    
    def test_sdk_initialization(self, integration_config):
        """Test SDK initialization with real configuration"""
        sdk = OktaAISDK(integration_config)
        
        assert sdk.config.okta_domain == integration_config.okta_domain
        assert sdk.config.client_id == integration_config.client_id
        assert sdk.token_exchange is not None
        assert sdk.cross_app_access is not None
    
    def test_token_format_validation(self, integration_sdk):
        """Test token format validation with real tokens"""
        # Test with a valid JWT format (this won't be a real token, just valid format)
        valid_format_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.EkN-DOsnsuRjRO6BxXemmJDm3HbxrbRzXglbN2S4sOkopdU4IsDxTI8jO19W_A4K8ZPJijNLis4EZsHeY559a4DFOd50_OqgH58ERTqYZyhtFJh3w9H5LvjXtuf4nKuqhUzVMEjxMyS_97U3qgf0HjI_ra6FbfggUj2Gdxjry1-VnIHtxyjyBXUclAsYeF06pHyMikYh9Qd3hGhzrYlMitoyKfvw3lB9VdF8NZpxjVuvY0OpY5zp8dWvfV_zXf1H3d-V5_udGmq8aJ0zF0bVnM9zDsT0vSvUuiyOsVv5iM1kI5r8TJNG5wJ3-TRK5d-6P-p_cV7M2P2QjGFpp8Q"
        
        # Test format validation
        is_valid = integration_sdk.token_exchange.validate_token_format(valid_format_token)
        assert is_valid is True
        
        # Test with invalid format
        invalid_token = "invalid.token"
        is_valid = integration_sdk.token_exchange.validate_token_format(invalid_token)
        assert is_valid is False
    
    def test_config_update(self, integration_sdk):
        """Test configuration update"""
        original_timeout = integration_sdk.config.timeout
        
        # Update timeout
        integration_sdk.update_config({"timeout": 60000})
        
        assert integration_sdk.config.timeout == 60000
        assert integration_sdk.config.client_id == integration_sdk.config.client_id  # Should remain unchanged
        
        # Restore original timeout
        integration_sdk.update_config({"timeout": original_timeout})
        assert integration_sdk.config.timeout == original_timeout
    
    @pytest.mark.skip(reason="Requires valid access token")
    def test_token_exchange_with_real_token(self, integration_sdk):
        """Test token exchange with real access token"""
        # This test requires a valid access token from environment
        access_token = os.getenv("TEST_ACCESS_TOKEN")
        if not access_token:
            pytest.skip("TEST_ACCESS_TOKEN environment variable not set")
        
        request = TokenExchangeRequest(
            subject_token=access_token,
            subject_token_type="urn:ietf:params:oauth:token-type:access_token",
            audience="https://api.example.com",
            scope="read"
        )
        
        try:
            result = integration_sdk.token_exchange.exchange_token(request)
            assert result.access_token is not None
            assert result.token_type == "Bearer"
            assert result.issued_token_type is not None
        except SDKError as e:
            # This might fail if the token is expired or invalid
            assert e.code in ["TOKEN_EXCHANGE_FAILED", "TOKEN_EXCHANGE_ERROR"]
    
    @pytest.mark.skip(reason="Requires valid ID token")
    def test_id_jag_exchange_with_real_token(self, integration_sdk):
        """Test ID-JAG token exchange with real ID token"""
        # This test requires a valid ID token from environment
        id_token = os.getenv("TEST_ID_TOKEN")
        if not id_token:
            pytest.skip("TEST_ID_TOKEN environment variable not set")
        
        try:
            result = integration_sdk.cross_app_access.exchange_id_token(
                id_token=id_token,
                audience="http://localhost:5001"
            )
            assert result.access_token is not None
            assert result.token_type == "Bearer"
            assert result.issued_token_type == "urn:ietf:params:oauth:token-type:id-jag"
        except SDKError as e:
            # This might fail if the token is expired or invalid
            assert e.code in ["ID_JAG_TOKEN_EXCHANGE_FAILED", "ID_JAG_TOKEN_EXCHANGE_ERROR", "MISSING_CLIENT_SECRET"]
    
    def test_error_handling_invalid_domain(self):
        """Test error handling with invalid domain"""
        config = OktaAIConfig(
            okta_domain="https://invalid-domain.okta.com",
            client_id="test_client_id"
        )
        
        with pytest.raises(ValueError):
            OktaAISDK(config)
    
    def test_error_handling_missing_credentials(self):
        """Test error handling with missing credentials"""
        config = OktaAIConfig(
            okta_domain="https://test.okta.com",
            client_id=""  # Empty client ID
        )
        
        with pytest.raises(ValueError):
            OktaAISDK(config)


