"""
Tests for core SDK functionality
"""

import pytest
from okta_ai_sdk import OktaAISDK, OktaAIConfig, SDKError


class TestOktaAIConfig:
    """Test OktaAIConfig class"""
    
    def test_config_creation(self):
        """Test basic config creation"""
        config = OktaAIConfig(
            okta_domain="https://test.okta.com",
            client_id="test_client_id"
        )
        
        assert config.okta_domain == "https://test.okta.com"
        assert config.client_id == "test_client_id"
        assert config.client_secret is None
        assert config.authorization_server_id == "default"
        assert config.timeout == 30000
        assert config.retry_attempts == 3
    
    def test_config_with_all_fields(self):
        """Test config creation with all fields"""
        config = OktaAIConfig(
            okta_domain="https://test.okta.com",
            client_id="test_client_id",
            client_secret="test_secret",
            authorization_server_id="custom",
            timeout=60000,
            retry_attempts=5
        )
        
        assert config.okta_domain == "https://test.okta.com"
        assert config.client_id == "test_client_id"
        assert config.client_secret == "test_secret"
        assert config.authorization_server_id == "custom"
        assert config.timeout == 60000
        assert config.retry_attempts == 5


class TestSDKError:
    """Test SDKError class"""
    
    def test_error_creation(self):
        """Test basic error creation"""
        error = SDKError("Test error", "TEST_ERROR")
        
        assert str(error) == "[TEST_ERROR] Test error"
        assert error.message == "Test error"
        assert error.code == "TEST_ERROR"
        assert error.status_code is None
        assert error.details == {}
    
    def test_error_with_status_code(self):
        """Test error creation with status code"""
        error = SDKError("Test error", "TEST_ERROR", 400)
        
        assert error.status_code == 400
    
    def test_error_with_details(self):
        """Test error creation with details"""
        details = {"field": "value"}
        error = SDKError("Test error", "TEST_ERROR", 400, details)
        
        assert error.details == details
    
    def test_error_to_dict(self):
        """Test error to dictionary conversion"""
        details = {"field": "value"}
        error = SDKError("Test error", "TEST_ERROR", 400, details)
        
        expected = {
            "message": "Test error",
            "code": "TEST_ERROR",
            "status_code": 400,
            "details": details
        }
        
        assert error.to_dict() == expected


class TestOktaAISDK:
    """Test OktaAISDK class"""
    
    def test_sdk_initialization(self, mock_config):
        """Test SDK initialization"""
        sdk = OktaAISDK(mock_config)
        
        assert sdk.config == mock_config
        assert sdk.token_exchange is not None
        assert sdk.cross_app_access is not None
    
    def test_sdk_initialization_invalid_domain(self):
        """Test SDK initialization with invalid domain"""
        config = OktaAIConfig(
            okta_domain="invalid-domain",
            client_id="test_client_id"
        )
        
        with pytest.raises(ValueError, match="okta_domain must be a valid URL"):
            OktaAISDK(config)
    
    def test_sdk_initialization_missing_domain(self):
        """Test SDK initialization with missing domain"""
        config = OktaAIConfig(
            okta_domain="",
            client_id="test_client_id"
        )
        
        with pytest.raises(ValueError, match="okta_domain is required"):
            OktaAISDK(config)
    
    def test_sdk_initialization_missing_client_id(self):
        """Test SDK initialization with missing client ID"""
        config = OktaAIConfig(
            okta_domain="https://test.okta.com",
            client_id=""
        )
        
        with pytest.raises(ValueError, match="client_id is required"):
            OktaAISDK(config)
    
    def test_sdk_config_normalization(self):
        """Test SDK config normalization"""
        config = OktaAIConfig(
            okta_domain="https://test.okta.com/",  # Trailing slash
            client_id="test_client_id"
        )
        
        sdk = OktaAISDK(config)
        
        # Should remove trailing slash
        assert sdk.config.okta_domain == "https://test.okta.com"
        assert sdk.config.authorization_server_id == "default"
        assert sdk.config.timeout == 30000
        assert sdk.config.retry_attempts == 3
    
    def test_sdk_update_config(self, mock_config):
        """Test SDK config update"""
        sdk = OktaAISDK(mock_config)
        
        # Update timeout
        sdk.update_config({"timeout": 60000})
        
        assert sdk.config.timeout == 60000
        assert sdk.config.client_id == "test_client_id"  # Should remain unchanged
    
    def test_sdk_get_config(self, mock_config):
        """Test getting SDK config"""
        sdk = OktaAISDK(mock_config)
        
        config = sdk.get_config()
        
        assert config == mock_config
        assert config is not sdk.config  # Should be a copy
    
    def test_sdk_create_error(self):
        """Test SDK static error creation"""
        error = OktaAISDK.create_error("Test error", "TEST_ERROR", 400)
        
        assert isinstance(error, SDKError)
        assert error.message == "Test error"
        assert error.code == "TEST_ERROR"
        assert error.status_code == 400


