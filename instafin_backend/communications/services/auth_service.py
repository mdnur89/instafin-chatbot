from django.core.exceptions import ValidationError
from django.conf import settings
import httpx
import json
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ChatAuthenticationService:
    """Service for handling chat authentication with Instafin API"""
    
    def __init__(self):
        self.base_url = settings.INSTAFIN_API_BASE_URL
        self.api_username = settings.INSTAFIN_API_USERNAME
        self.api_password = settings.INSTAFIN_API_PASSWORD
        print("\n=== ChatAuthenticationService Initialized ===")
        print(f"API Base URL: {self.base_url}")
        
    async def validate_account(self, account_identifier: str) -> Optional[Dict[str, Any]]:
        """Validate account exists in Instafin system"""
        try:
            print("\n=== Making API Call ===")
            print(f"Endpoint: {self.base_url}/submit/account.LookupDebts")
            
            payload = {
                "accounts": [account_identifier],
                "debts": {}  # Required field per API spec
            }
            print(f"Request Payload: {json.dumps(payload, indent=2)}")
            
            async with httpx.AsyncClient() as client:
                print("\nSending request...")
                auth = httpx.BasicAuth(self.api_username, self.api_password)
                
                response = await client.post(
                    f"{self.base_url}/submit/account.LookupDebts",
                    json=payload,
                    auth=auth,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"\nResponse Status: {response.status_code}")
                print(f"Response Headers: {dict(response.headers)}")
                print(f"Response Body: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    print("✅ API call successful")
                    print(f"Response Data: {json.dumps(data, indent=2)}")
                    return data
                    
                elif response.status_code == 400:
                    errors = response.json()
                    print("❌ Validation Error:")
                    for error in errors:
                        print(f"  - Field: {error.get('fieldRef')}")
                        print(f"  - Message: {error.get('message')}")
                    return None
                    
                elif response.status_code == 401:
                    print("❌ Authentication Error: Session invalid/expired")
                    raise ValidationError("API session invalid or expired")
                    
                elif response.status_code == 403:
                    print("❌ Permission Error: Insufficient permissions")
                    raise ValidationError("Insufficient permissions")
                    
                else:
                    print(f"❌ Unexpected API Error: {response.status_code}")
                    return None
                    
        except Exception as e:
            print(f"❌ API Call Error: {str(e)}")
            print(f"Error Type: {type(e).__name__}")
            return None

    async def authenticate_user(self, account_identifier: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with their account identifier"""
        try:
            print(f"\n=== Starting Authentication for Account: {account_identifier} ===")
            
            account_data = await self.validate_account(account_identifier)
            if not account_data:
                print("❌ Account validation failed")
                return None
                
            if not account_data.get('accounts'):
                print("❌ No account data in response")
                return None
                
            print("✅ Account validated successfully")
            print(f"Account Data: {json.dumps(account_data, indent=2)}")
            
            return {
                'account_id': account_identifier,
                'is_authenticated': True,
                'debts': account_data.get('debts', {})
            }
            
        except Exception as e:
            print(f"❌ Authentication Error: {str(e)}")
            return None 