import requests
from requests.auth import HTTPBasicAuth
from typing import Union, Dict, Any
from instafin_backend.settings import INSTAFIN_API_BASE_URL,INSTAFIN_API_PASSWORD,INSTAFIN_API_USERNAME

class LoanAccountAPIClient:
    BASE_URL = f"{INSTAFIN_API_BASE_URL}/submit/instafin.LookupLoanAccount" 
    AUTH_USERNAME = INSTAFIN_API_USERNAME
    AUTH_PASSWORD = INSTAFIN_API_PASSWORD

    @classmethod
    def get_loan_account_data(cls, identifier: Dict[str, str]) -> Dict[str, Any]:
        """
        Fetch loan account data using one of the allowed identifiers.

        :param identifier: A dictionary containing one of the following:
            - {"ID": "A000006"}
            - {"accountID": "3770"}
            - {"externalAccountNumber": "1234567890"}
        :return: A dictionary containing the parsed loan account data.
        """
        url = f"{cls.BASE_URL}/loan-account/lookup"  # Replace with the actual endpoint
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(
                url,
                json=identifier,
                headers=headers,
                auth=HTTPBasicAuth(cls.AUTH_USERNAME, cls.AUTH_PASSWORD)
            )
            response.raise_for_status()
            return cls.parse_response(response.json())
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    @staticmethod
    def parse_response(response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the loan account response for easier access to key fields.

        :param response: The API response in raw JSON format.
        :return: A dictionary with parsed fields.
        """
        try:
            loan_account = response.get("loanAccount", {})
            client = loan_account.get("client", {})
            personal_info = client.get("personal", {})
            loan_product = response.get("loanProduct", {})
            parsed_data = {
                "account_id": response.get("accountID"),
                "external_account_number": response.get("externalAccountNumber"),
                "loan_amount": loan_account.get("loanAmount"),
                "interest_rate": loan_account.get("interestRate"),
                "loan_status": loan_account.get("accountStatus"),
                "client_name": client.get("name"),
                "client_email": client.get("email"),
                "client_phone": client.get("mobile", {}).get("number"),
                "client_address": client.get("address", {}).get("street1"),
                "loan_product_name": loan_product.get("name"),
                "loan_product_description": loan_product.get("description"),
                "instalments": loan_account.get("instalments", []),
                "transactions": response.get("transactions", []),
                "guarantors": loan_account.get("optionalFields", {}).get("guarantors", []),
              #  "personal_info": loan_account.get("personal", {}).get("personal", [])
            }
            return parsed_data
        except Exception as e:
            return {"error": f"Error parsing response: {str(e)}"}
        

class LoanAccountSearchAPIClient:
    BASE_URL = f"{INSTAFIN_API_BASE_URL}/submit/instafin.SearchAllAccounts" 
    AUTH_USERNAME = INSTAFIN_API_USERNAME
    AUTH_PASSWORD = INSTAFIN_API_PASSWORD


    @classmethod
    def search_accounts(cls, organisation_id: str, client_id: str, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        Search for loan accounts using organisation ID and client ID.

        :param organisation_id: The ID of the organization to filter accounts.
        :param client_id: The client ID to filter accounts.
        :param limit: Number of results to fetch (default is 100).
        :param offset: Pagination offset (default is 0).
        :return: A dictionary containing the search results or an error message.
        """
        url = f"{cls.BASE_URL}/accounts/search"  # Replace with the actual endpoint
        headers = {"Content-Type": "application/json"}
        payload = {
            "filter": {
                "organisation": organisation_id,
                "clients": [client_id]
            },
            "pagination": {
                "limit": limit,
                "offset": offset
            }
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                auth=HTTPBasicAuth(cls.AUTH_USERNAME, cls.AUTH_PASSWORD)
            )
            response.raise_for_status()
            return cls.parse_response(response.json())
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    @staticmethod
    def parse_response(response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the account search response for easier access to key fields.

        :param response: The API response in raw JSON format.
        :return: A dictionary with parsed fields.
        """
        try:
            items = response.get("items", [])
            parsed_items = [
                {
                    "account_id": item.get("accountId"),
                    "account_type_id": item.get("accountTypeId"),
                    "account_type_name": item.get("accountTypeName"),
                    "account_status": item.get("status"),
                    "account_status_name": item.get("accountStatusName"),
                    "client_id": item.get("clientId"),
                    "client_name": item.get("clientName"),
                    "client_external_id": item.get("clientExternalId"),
                    "product_name": item.get("productName"),
                    "product_type_name": item.get("productTypeName"),
                    "external_account_number": item.get("externalAccountNumber"),
                    "balance": item.get("balance"),
                    "created_on": item.get("createdOn"),
                    "currency": item.get("currency"),
                }
                for item in items
            ]
            return {
                "filter": response.get("filter", {}),
                "accounts": parsed_items,
                "pagination": response.get("pagination", {}),
            }
        except Exception as e:
            return {"error": f"Error parsing response: {str(e)}"}
        
class ClientLookupAPIClient:
    BASE_URL = f"{INSTAFIN_API_BASE_URL}/submit/instafin.LookupClient"
    AUTH_USERNAME = INSTAFIN_API_USERNAME
    AUTH_PASSWORD = INSTAFIN_API_PASSWORD

    @classmethod
    def lookup_client(cls, identifier: str, is_external_id: bool = True) -> Dict[str, Any]:
        """
        Lookup client using either Client External Identifier or Client Internal Identifier.

        :param identifier: The identifier to lookup the client. Could be either external ID or internal client ID.
        :param is_external_id: Boolean to specify if the identifier is external ID. Default is True.
        :return: A dictionary containing the client data or an error message.
        """
        url = f"{cls.BASE_URL}/client/lookup"
        headers = {"Content-Type": "application/json"}
        payload = {"ID": identifier} if is_external_id else {"clientID": identifier}

        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                auth=HTTPBasicAuth(cls.AUTH_USERNAME, cls.AUTH_PASSWORD)
            )
            response.raise_for_status()
            return cls.parse_response(response.json())
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    @staticmethod
    def parse_response(response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the client lookup response for easier access to key fields.

        :param response: The API response in raw JSON format.
        :return: A dictionary with parsed fields.
        """
        try:
            client_data = response.get("client", {})
            loans = response.get("loans", [])
            deposits = response.get("deposits", [])
            guarantors = response.get("guarantors", [])
            permissions = response.get("permissions", {})

            parsed_client = {
                "ID": response.get("ID"),
                "clientID": response.get("clientID"),
                "name": client_data.get("name"),
                "status": client_data.get("clientStatus"),
                "email": client_data.get("email"),
                "mobile": client_data.get("mobile", {}).get("number"),
                "address": client_data.get("address", {}).get("street1"),
                "city": client_data.get("address", {}).get("city"),
                "state": client_data.get("address", {}).get("state"),
                "country": client_data.get("address", {}).get("country"),
                "loans": [
                    {
                        "ID": loan.get("ID"),
                        "productName": loan.get("productName"),
                        "amount": loan.get("amount"),
                        "principalBalance": loan.get("principalBalance"),
                        "status": loan.get("status"),
                        "appliedDate": loan.get("appliedDate"),
                        "startDate": loan.get("startDate"),
                        "closeDate": loan.get("closeDate"),
                    }
                    for loan in loans
                ],
                "deposits": [
                    {
                        "ID": deposit.get("ID"),
                        "productName": deposit.get("productName"),
                        "balance": deposit.get("balance"),
                        "status": deposit.get("status"),
                        "appliedDate": deposit.get("appliedDate"),
                        "startDate": deposit.get("startDate"),
                        "endDate": deposit.get("endDate"),
                    }
                    for deposit in deposits
                ],
                "guarantors": [
                    {
                        "ID": guarantor.get("guarantorID"),
                        "name": guarantor.get("name"),
                        "relationshipToClient": guarantor.get("relationshipToClientLabel"),
                    }
                    for guarantor in guarantors
                ],
                "permissions": {
                    "allowEdit": permissions.get("allowEdit"),
                    "allowCreateLoanAccount": permissions.get("allowCreateLoanAccount"),
                    "allowCreateDepositAccount": permissions.get("allowCreateDepositAccount"),
                },
            }

            return parsed_client
        except Exception as e:
            return {"error": f"Error parsing response: {str(e)}"}