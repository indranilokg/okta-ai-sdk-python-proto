"""
Cross-App Access Client

Implements Identity Assertion Authorization Grant (ID-JAG) for secure cross-application access
"""

import json
import base64
import time
from typing import Dict, Any, Optional

import requests
import jwt
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError, PyJWKError

from ..types import (
    OktaAIConfig,
    IdJagTokenRequest,
    IdJagTokenResponse,
    IdJagTokenVerificationOptions,
    IdJagTokenVerificationResult,
    SDKError,
)


class CrossAppAccessClient:
    """Cross-App Access Client for Identity Assertion Authorization Grant (ID-JAG)"""

    def __init__(self, config: OktaAIConfig):
        """Initialize the Cross-App Access Client"""
        self.config = config
        self.session = requests.Session()
        self.session.timeout = config.timeout / 1000 if config.timeout else 30  # Convert ms to seconds

    def exchange_id_token_for_id_jag(self, request: IdJagTokenRequest) -> IdJagTokenResponse:
        """
        Exchange an Okta ID token for an ID-JAG token
        Based on RFC 8693 (OAuth 2.0 Token Exchange) with ID-JAG extension
        """
        try:
            print("🔄 Exchanging ID token for ID-JAG token...")
            print(f"📍 Audience: {request.audience}")
            print(f"🆔 Client ID: {request.client_id}")

            # Prepare the token exchange request - Cross App Access uses org auth server
            token_exchange_url = f"{self.config.okta_domain}/oauth2/v1/token"
            
            form_data = {
                'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
                'requested_token_type': 'urn:ietf:params:oauth:token-type:id-jag',
                'subject_token': request.subject_token,
                'subject_token_type': 'urn:ietf:params:oauth:token-type:id_token',
                'audience': request.audience,
                'client_id': request.client_id,
                'client_secret': request.client_secret,
            }

            print(f"🌐 Making ID-JAG token exchange request to: {token_exchange_url}")

            response = self.session.post(
                token_exchange_url,
                data=form_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

            response.raise_for_status()
            response_data = response.json()

            print("✅ ID-JAG token exchange successful")
            print(f"🎯 Issued token type: {response_data.get('issued_token_type')}")
            print(f"⏰ Expires in: {response_data.get('expires_in', 'N/A')} seconds")

            return IdJagTokenResponse(**response_data)

        except requests.exceptions.RequestException as e:
            print(f"❌ ID-JAG token exchange failed: {e}")
            
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error_description', error_data.get('error', 'Unknown error'))
                    raise self._create_error(
                        f"ID-JAG token exchange failed: {error_message}",
                        'ID_JAG_TOKEN_EXCHANGE_FAILED',
                        e.response.status_code,
                        error_data
                    )
                except (ValueError, KeyError):
                    raise self._create_error(
                        f"ID-JAG token exchange failed: {e.response.text}",
                        'ID_JAG_TOKEN_EXCHANGE_FAILED',
                        e.response.status_code
                    )
            
            raise self._create_error(
                f"ID-JAG token exchange failed: {str(e)}",
                'ID_JAG_TOKEN_EXCHANGE_ERROR'
            )

    def verify_id_jag_token(
        self, 
        token: str, 
        options: IdJagTokenVerificationOptions
    ) -> IdJagTokenVerificationResult:
        """
        Verify an ID-JAG token using the issuer's public keys
        """
        try:
            print("🔍 Verifying ID-JAG token...")
            print(f"📍 Expected Issuer: {options.issuer}")
            print(f"🎯 Expected Audience: {options.audience}")

            # Determine JWKS URI
            jwks_uri = options.jwks_uri or f"{options.issuer}/oauth2/v1/keys"
            print(f"🔑 JWKS URI: {jwks_uri}")

            # Create JWK client
            jwks_client = PyJWKClient(jwks_uri)

            # Get the signing key
            signing_key = jwks_client.get_signing_key_from_jwt(token)

            # Verify the token
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256", "ES256"],
                audience=options.audience,
                issuer=options.issuer,
                options={"verify_exp": True, "verify_aud": True, "verify_iss": True}
            )

            print("✅ ID-JAG token verified successfully")
            print(f"👤 Subject: {payload.get('sub')}")
            print(f"📧 Email: {payload.get('email', 'N/A')}")
            print(f"🎯 Audience: {payload.get('aud')}")
            print(f"📍 Issuer: {payload.get('iss')}")
            print(f"⏰ Expires: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(payload.get('exp', 0)))}")

            return IdJagTokenVerificationResult(
                valid=True,
                payload=payload,
                sub=payload.get('sub'),
                email=payload.get('email'),
                aud=payload.get('aud'),
                iss=payload.get('iss'),
                exp=payload.get('exp')
            )

        except (InvalidTokenError, PyJWKError) as e:
            print(f"❌ ID-JAG token verification failed: {e}")
            return IdJagTokenVerificationResult(
                valid=False,
                error=str(e)
            )
        except Exception as e:
            print(f"❌ ID-JAG token verification failed: {e}")
            return IdJagTokenVerificationResult(
                valid=False,
                error=f"Unknown verification error: {str(e)}"
            )

    def validate_id_jag_token_format(self, token: str) -> bool:
        """
        Validate that a token looks like an ID-JAG token (basic format check)
        """
        try:
            # Basic JWT format validation (header.payload.signature)
            parts = token.split('.')
            if len(parts) != 3:
                return False

            # Try to decode the header and payload (basic validation)
            header = json.loads(base64.urlsafe_b64decode(parts[0] + '==').decode('utf-8'))
            payload = json.loads(base64.urlsafe_b64decode(parts[1] + '==').decode('utf-8'))

            # Check for required claims
            return bool(header.get('alg') and payload.get('sub') and payload.get('aud') and payload.get('exp'))
        except Exception:
            return False

    def exchange_id_token(self, id_token: str, audience: str) -> IdJagTokenResponse:
        """
        Exchange ID token for ID-JAG token using SDK configuration
        Convenience method that uses the SDK's client credentials
        """
        if not self.config.client_secret:
            raise self._create_error(
                'Client secret is required for ID-JAG token exchange',
                'MISSING_CLIENT_SECRET'
            )

        request = IdJagTokenRequest(
            subject_token=id_token,
            audience=audience,
            client_id=self.config.client_id,
            client_secret=self.config.client_secret
        )

        return self.exchange_id_token_for_id_jag(request)

    def verify_id_jag_token_with_config(
        self, 
        token: str, 
        audience: str
    ) -> IdJagTokenVerificationResult:
        """
        Verify ID-JAG token using SDK configuration
        Convenience method that uses the SDK's issuer configuration
        """
        options = IdJagTokenVerificationOptions(
            issuer=self.config.okta_domain,
            audience=audience
        )

        return self.verify_id_jag_token(token, options)

    def _create_error(
        self, 
        message: str, 
        code: str, 
        status_code: Optional[int] = None, 
        details: Optional[Dict[str, Any]] = None
    ) -> SDKError:
        """Create a custom error"""
        return SDKError(message, code, status_code, details)

