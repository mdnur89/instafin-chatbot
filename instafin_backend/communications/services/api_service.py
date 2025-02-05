from django.conf import settings
import httpx
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class InstafinAPIService:
    """Service for interacting with Instafin API"""
    
    def __init__(self):
        self.base_url = settings.INSTAFIN_API_BASE_URL
        self.auth = httpx.BasicAuth(
            settings.INSTAFIN_API_USERNAME, 
            settings.INSTAFIN_API_PASSWORD
        )
        
    async def lookup_debts(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Fetch debts for an account"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/submit/account.LookupDebts",
                    json={"accounts": [account_id]},
                    auth=self.auth,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data and data.get('accounts'):
                        return self._format_debt_response(data['accounts'][0])
                return None
                
        except Exception as e:
            logger.error(f"Error looking up debts: {str(e)}")
            return None
            
    def _format_debt_response(self, account_data: Dict[str, Any]) -> str:
        """Format debt information into readable message"""
        response = f"Account Summary for {account_data.get('customer_name', 'Customer')}\n"
        response += f"Account: {account_data.get('external_id', 'N/A')}\n\n"
        
        debts = account_data.get('debts', [])
        if not debts:
            response += "No active debts found."
            return response
            
        for debt in debts:
            response += f"Loan ID: {debt.get('id', 'N/A')}\n"
            response += f"Status: {debt.get('status', 'N/A')}\n"
            response += f"Principal: {debt.get('principal', 0):,.2f}\n"
            response += f"Balance: {debt.get('balance', 0):,.2f}\n"
            response += f"Due Date: {debt.get('due_date', 'N/A')}\n"
            response += "-" * 40 + "\n"
            
        return response 