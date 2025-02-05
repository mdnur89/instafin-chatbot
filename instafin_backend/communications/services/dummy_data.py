from typing import Dict, Any
from datetime import datetime, timedelta
import random

class DummyDataStore:
    """Dummy data store for testing chat functionality"""
    
    # Sample account data
    ACCOUNTS = {
        "1113": {
            "account_id": "1113",
            "external_id": "ACC001",
            "customer_name": "John Doe",
            "loan_amount": 50000.00,
            "remaining_balance": 42500.00,
            "next_payment_date": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
            "payment_amount": 2500.00,
            "loan_status": "active"
        },
        "1114": {
            "account_id": "1114",
            "external_id": "ACC002",
            "customer_name": "Jane Smith",
            "loan_amount": 75000.00,
            "remaining_balance": 65000.00,
            "next_payment_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "payment_amount": 3750.00,
            "loan_status": "active"
        }
    }

    # Sample loan statements
    LOAN_STATEMENTS = {
        "1113": [
            {
                "date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                "description": "Monthly Payment",
                "amount": 2500.00,
                "balance": 42500.00
            },
            {
                "date": (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d"),
                "description": "Monthly Payment",
                "amount": 2500.00,
                "balance": 45000.00
            }
        ]
    }

    # Sample notifications
    NOTIFICATIONS = {
        "1113": [
            {
                "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                "type": "payment_reminder",
                "message": "Your next payment is due in 15 days"
            },
            {
                "date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                "type": "promotion",
                "message": "You're eligible for a loan top-up!"
            }
        ]
    }

    @classmethod
    def get_account(cls, account_id: str) -> Dict[str, Any]:
        """Get account data by ID"""
        return cls.ACCOUNTS.get(account_id)

    @classmethod
    def get_loan_statement(cls, account_id: str) -> str:
        """Get formatted loan statement"""
        account = cls.get_account(account_id)
        statements = cls.LOAN_STATEMENTS.get(account_id, [])
        
        if not account or not statements:
            return "No loan statement available."

        response = f"Loan Statement for {account['customer_name']}\n"
        response += f"Account: {account['external_id']}\n"
        response += f"Total Loan Amount: ${account['loan_amount']:,.2f}\n"
        response += f"Remaining Balance: ${account['remaining_balance']:,.2f}\n\n"
        response += "Recent Transactions:\n"
        response += "-" * 50 + "\n"
        
        for stmt in statements:
            response += f"Date: {stmt['date']}\n"
            response += f"Description: {stmt['description']}\n"
            response += f"Amount: ${stmt['amount']:,.2f}\n"
            response += f"Balance: ${stmt['balance']:,.2f}\n"
            response += "-" * 50 + "\n"
            
        return response

    @classmethod
    def get_repayment_schedule(cls, account_id: str) -> str:
        """Get formatted repayment schedule"""
        account = cls.get_account(account_id)
        if not account:
            return "No repayment schedule available."

        response = f"Repayment Schedule for {account['customer_name']}\n"
        response += f"Account: {account['external_id']}\n"
        response += f"Next Payment Date: {account['next_payment_date']}\n"
        response += f"Payment Amount: ${account['payment_amount']:,.2f}\n"
        response += f"Remaining Balance: ${account['remaining_balance']:,.2f}\n"
        
        return response

    @classmethod
    def get_account_summary(cls, account_id: str) -> str:
        """Get formatted account summary"""
        account = cls.get_account(account_id)
        if not account:
            return "No account summary available."

        response = f"Account Summary for {account['customer_name']}\n"
        response += f"Account: {account['external_id']}\n"
        response += f"Loan Status: {account['loan_status'].title()}\n"
        response += f"Original Loan Amount: ${account['loan_amount']:,.2f}\n"
        response += f"Current Balance: ${account['remaining_balance']:,.2f}\n"
        response += f"Next Payment: ${account['payment_amount']:,.2f} due on {account['next_payment_date']}\n"
        
        return response

    @classmethod
    def get_notifications(cls, account_id: str) -> str:
        """Get formatted notifications"""
        notifications = cls.NOTIFICATIONS.get(account_id, [])
        if not notifications:
            return "No notifications available."

        response = "Recent Notifications:\n"
        response += "-" * 50 + "\n"
        
        for notif in notifications:
            response += f"Date: {notif['date']}\n"
            response += f"Type: {notif['type'].replace('_', ' ').title()}\n"
            response += f"Message: {notif['message']}\n"
            response += "-" * 50 + "\n"
            
        return response 