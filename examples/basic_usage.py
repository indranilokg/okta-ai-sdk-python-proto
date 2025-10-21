#!/usr/bin/env python3
"""
Basic usage example for Okta AI SDK

This example demonstrates basic token exchange and cross-app access functionality.
"""

import os
import sys
from typing import Dict, Any

# Add the src directory to the path so we can import the SDK
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from okta_ai_sdk import (
    OktaAISDK,
    OktaAIConfig,
    TokenExchangeRequest,
    TokenVerificationOptions,
    IdJagTokenRequest,
)


def main():
    """Main example function"""
    
    # Configuration - replace with your actual values
    config = OktaAIConfig(
        okta_domain="https://ijtestcustom.oktapreview.com",
        client_id="0oamzrqsmecaqzqWb1d7",
        client_secret="sjDxEIbzCmXxcIA5wKWnkg3X8Sab9ZM1-l3nJ2mpC9xItS4FQwVzsPqqNLIp_Yfb",  # Optional
        authorization_server_id="ausmzrly3zjFPEJOH1d7"  # Optional, defaults to 'default'
    )
    
    # Initialize the SDK
    sdk = OktaAISDK(config)
    
    print("🚀 Okta AI SDK initialized successfully!")
    print(f"📍 Okta Domain: {sdk.config.okta_domain}")
    print(f"🆔 Client ID: {sdk.config.client_id}")
    print()
    
    # Example 1: Token Exchange
    print("=== Token Exchange Example ===")
    try:
        # This would be your actual access token
        access_token = "eyJraWQiOiJrOUExMHFUQndJWDkxR0pHbWVYS3N2aFlfOGRjdGhpREtQcUVTSFJ1WDRrIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULlJDTThyb3RwYThDS2NNZ2FTRmQ0NzR5aklOM2U5anZmQzRSeTI5M3h2NEUiLCJpc3MiOiJodHRwczovL2FjbWUudHdpc2VjLmNvbS9vYXV0aDIvYXVzbXpybTFmcHJ3U09PSHAxZDciLCJhdWQiOiJjb20uYXBpLnN0b3JlLmFjbWUiLCJpYXQiOjE3NjA5MDk5MzcsImV4cCI6MTc2MDkxMzUzNywiY2lkIjoiMG9hNmJxa2w1NjQyQWV0MU8xZDciLCJ1aWQiOiIwMHU2Y2IxdWFnV3hacE5kZjFkNyIsInNjcCI6WyJvcGVuaWQiLCJzdG9yZTp2aWV3Iiwic3RvcmU6cHVyY2hhc2UiXSwiYXV0aF90aW1lIjoxNzYwOTA5OTM2LCJzdWIiOiJkY3JhbmVAYXRrby5lbWFpbCJ9.eYZrsNhsPtwYjv6DF0guTjf8Jb-YWSnBO47mGuqdejpzn2XnnDHy71UYz5FWbuEBW6daYNuecqX-H0F5H7gLad5qFnrDSdFVI0kqAhrdeP-7D4AnPo8rw1OgM3Ix-EkstgIcqZrLfTJ5eLhqKZVCF-BqVZh8aB0ngoYwsMqi_9EHnLHY-wiJD1zl5SD9Rw-dSQ7cKwFy8JxWmT8Ej6J2Z2c7ddpnNa4VWRDaGKG2WwxQZUd-WWjfax2zu69KDY7qAnLeRzNQJJZ94en1-dwLG0pE0SXQ-YP8UbQUz_c7TfcZSJ97M9wu9i4xBvB1sTVgKL-c9X6vpMv-H_DIvsC4rw"
        
        # Create token exchange request
        token_request = TokenExchangeRequest(
            subject_token=access_token,
            subject_token_type="urn:ietf:params:oauth:token-type:access_token",
            audience="com.api.payment.acme",
            scope="payments:manage payments:view"
        )
        
        # Exchange the token
        result = sdk.token_exchange.exchange_token(token_request)
        print(f"✅ Token exchange successful!")
        print(f"🎯 New token: {result.access_token}")
    
        print(f"⏰ Expires in: {result.expires_in} seconds")
        
        # Verify the exchanged token
        print("\n🔍 Verifying exchanged token...")
        verification_options = TokenVerificationOptions(
            issuer=f"{sdk.config.okta_domain}/oauth2/{sdk.config.authorization_server_id}",
            audience="com.api.payment.acme",
            expected_scope="payments:view"  # Validate subset of scopes (token has more scopes)
        )
        
        verification_result = sdk.token_exchange.verify_token(
            token=result.access_token,
            options=verification_options
        )
        
        if verification_result.valid:
            print(f"✅ Exchanged token verified successfully!")
            print(f"👤 Subject: {verification_result.sub}")
            print(f"🎯 Audience: {verification_result.aud}")
            print(f"📍 Issuer: {verification_result.iss}")
            print(f"🔐 Scope: {verification_result.scope}")
        else:
            print(f"❌ Token verification failed: {verification_result.error}")
        
    except Exception as e:
        print(f"❌ Token exchange failed: {e}")
    
    print()
    
    # Example 2: Cross-App Access (ID-JAG)
    print("=== Cross-App Access (ID-JAG) Example ===")
    try:
        # This would be your actual ID token
        id_token = "eyJraWQiOiIwOXJFQnJlZkpaNE9CMEg3UUx6TkVFN3I4WW1VZVRVUExCcHJGZmNiN05NIiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIwMHUxcnNqZWpidWV1UU5oQjFkNyIsImxvY2FsZSI6ImVuLVVTIiwiZW1haWwiOiJpbmRyYW5pbC5qaGFAb2t0YS5jb20iLCJ2ZXIiOjEsImlzcyI6Imh0dHBzOi8vaWp0ZXN0Y3VzdG9tLm9rdGFwcmV2aWV3LmNvbSIsImF1ZCI6IjBvYXA2YTNrcHV0VUh5VzFSMWQ3IiwiaWF0IjoxNzYwOTAzNDQ5LCJleHAiOjE3NjA5MDcwNDksImp0aSI6IklELldSX0paSTIwNFMxRWVhWEJmRi03UVVaMUI1NTNXR2tHWHVQMHozZENTVjgiLCJhbXIiOlsicHdkIl0sImlkcCI6IjAwbzFyc2plZmZPWkQ0M1I4MWQ3Iiwic2lkIjoiaWR4LVY2SnVLYVRRYTI4RFZWb2lvTFJ1QSIsInByZWZlcnJlZF91c2VybmFtZSI6ImluZHJhbmlsLmpoYUBva3RhLmNvbSIsImdpdmVuX25hbWUiOiJJbmRyYW5pbCIsImZhbWlseV9uYW1lIjoiSmhhIiwiem9uZWluZm8iOiJBbWVyaWNhL0xvc19BbmdlbGVzIiwidXBkYXRlZF9hdCI6MTc1NTE5NzQwOCwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJhdXRoX3RpbWUiOjE3NjA5MDM0NDgsImF0X2hhc2giOiJCcXpHaXJRc09DR3ppYXBoSlRWeEdBIn0.vQYnasWlhG6hWypLCJDrDyBmLPktKG-8Dh_CLNEQfuKpdNAzEQfd1MYlpsO65FAb3DDI0HD5XZSzSf4uBhSsoQgyDMPvx8PrVtqBLzm4Rpoc_ZysCV0LuVfepPvcJcIdU3twmSa-lSqdvSLDY-GyObU-0IRkj9dI_E7Jw3bnOOlaG-vuDwnJq_IwSFLVRiv2PB6p__uowjM7fSUlffTxBkSBIteN2YVyTDXYEB2dPU1UsBL6qNSU-D1hbFqZXlW3NAoXjvsF1ExXdVK0tha-_UP2ZqcmjvPLUIi5kytzVvs7lKVBs6Azu1bN_wiQszBUlnfSKYxhcKgVbxGIQuIW0A"
        target_audience = "http://localhost:5001"
        
        # Exchange ID token for ID-JAG token (convenience method)
        id_jag_result = sdk.cross_app_access.exchange_id_token(
            id_token=id_token,
            audience=target_audience
        )
        
        print(f"✅ ID-JAG token exchange successful!")
        print(f"🎯 ID-JAG token: {id_jag_result.access_token[:50]}...")
        print(f"⏰ Expires in: {id_jag_result.expires_in} seconds")
        
        # Verify the ID-JAG token
        verification_result = sdk.cross_app_access.verify_id_jag_token_with_config(
            token=id_jag_result.access_token,
            audience=target_audience
        )
        
        if verification_result.valid:
            print(f"✅ ID-JAG token verified successfully!")
            print(f"👤 Subject: {verification_result.sub}")
            print(f"📧 Email: {verification_result.email}")
        else:
            print(f"❌ ID-JAG token verification failed: {verification_result.error}")
            
    except Exception as e:
        print(f"❌ Cross-app access failed: {e}")
    
    print()
    
    # Example 3: Token Format Validation
    print("=== Token Format Validation Example ===")
    test_tokens = [
        "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.EkN-DOsnsuRjRO6BxXemmJDm3HbxrbRzXglbN2S4sOkopdU4IsDxTI8jO19W_A4K8ZPJijNLis4EZsHeY559a4DFOd50_OqgH58ERTqYZyhtFJh3w9H5LvjXtuf4nKuqhUzVMEjxMyS_97U3qgf0HjI_ra6FbfggUj2Gdxjry1-VnIHtxyjyBXUclAsYeF06pHyMikYh9Qd3hGhzrYlMitoyKfvw3lB9VdF8NZpxjVuvY0OpY5zp8dWvfV_zXf1H3d-V5_udGmq8aJ0zF0bVnM9zDsT0vSvUuiyOsVv5iM1kI5r8TJNG5wJ3-TRK5d-6P-p_cV7M2P2QjGFpp8Q",
        "invalid.token",
        "not.a.jwt.token",
    ]
    
    for i, token in enumerate(test_tokens, 1):
        is_valid = sdk.token_exchange.validate_token_format(token)
        print(f"Token {i}: {'✅ Valid' if is_valid else '❌ Invalid'}")


if __name__ == "__main__":
    main()
