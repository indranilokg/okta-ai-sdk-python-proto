"""
Main Okta AI SDK class

Provides unified access to Token Exchange and Cross-App Access functionality
"""

from typing import Optional
from urllib.parse import urlparse

from ..types import OktaAIConfig, SDKError
from ..token_exchange.client import TokenExchangeClient
from ..cross_app_access.client import CrossAppAccessClient


class OktaAISDK:
    """Main Okta AI SDK class providing unified access to all functionality"""

    def __init__(self, config: OktaAIConfig):
        """Initialize the Okta AI SDK"""
        self._validate_config(config)
        self._config = self._normalize_config(config)
        
        # Initialize sub-clients
        self.token_exchange = TokenExchangeClient(self._config)
        self.cross_app_access = CrossAppAccessClient(self._config)

    @property
    def config(self) -> OktaAIConfig:
        """Get the current SDK configuration"""
        return self._config

    def get_config(self) -> OktaAIConfig:
        """Get the current SDK configuration (alias for config property)"""
        return self.config

    def update_config(self, updates: dict) -> None:
        """Update SDK configuration"""
        new_config_dict = self._config.dict()
        new_config_dict.update(updates)
        new_config = OktaAIConfig(**new_config_dict)
        
        self._validate_config(new_config)
        self._config = self._normalize_config(new_config)
        
        # Reinitialize sub-clients with new config
        self.token_exchange = TokenExchangeClient(self._config)
        self.cross_app_access = CrossAppAccessClient(self._config)

    def _validate_config(self, config: OktaAIConfig) -> None:
        """Validate SDK configuration"""
        if not config.okta_domain:
            raise ValueError('okta_domain is required')
        if not config.client_id:
            raise ValueError('client_id is required')
        
        # Validate Okta domain format
        try:
            parsed = urlparse(config.okta_domain)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError('okta_domain must be a valid URL')
        except Exception as e:
            raise ValueError(f'okta_domain must be a valid URL: {e}')

    def _normalize_config(self, config: OktaAIConfig) -> OktaAIConfig:
        """Normalize configuration with defaults"""
        config_dict = config.dict()
        
        # Remove trailing slash from domain
        if config_dict['okta_domain'].endswith('/'):
            config_dict['okta_domain'] = config_dict['okta_domain'].rstrip('/')
        
        # Set defaults
        config_dict['authorization_server_id'] = config_dict.get('authorization_server_id') or 'default'
        config_dict['timeout'] = config_dict.get('timeout') or 30000  # 30 seconds
        config_dict['retry_attempts'] = config_dict.get('retry_attempts') or 3
        
        return OktaAIConfig(**config_dict)

    @staticmethod
    def create_error(
        message: str, 
        code: str, 
        status_code: Optional[int] = None, 
        details: Optional[dict] = None
    ) -> SDKError:
        """Create a custom error"""
        return SDKError(message, code, status_code, details)

