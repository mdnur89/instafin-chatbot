from enum import Enum
from typing import Optional, Dict, Any

class MenuOption(Enum):
    LOAN_STATEMENT = "1"
    REPAYMENT_SCHEDULE = "2"
    ACCOUNT_SUMMARY = "3"
    NOTIFICATIONS = "4"
    HELP = "help"
    EXIT = "exit"

class ChatMenuService:
    """Service for handling chat menu interactions"""
    
    MAIN_MENU = """
How can I help you today?

1. View Loan Statement
2. Check Repayment Schedule
3. View Account Summary
4. View Notifications

Type 'help' for assistance or 'exit' to end session.
"""

    async def handle_menu_selection(self, selection: str) -> Dict[str, Any]:
        """Process menu selection and return appropriate response"""
        try:
            option = MenuOption(selection.lower())
        except ValueError:
            return {
                'message': f"Invalid selection. {self.MAIN_MENU}",
                'action': None
            }

        if option == MenuOption.HELP:
            return {
                'message': self.MAIN_MENU,
                'action': None
            }
            
        if option == MenuOption.EXIT:
            return {
                'message': "Thank you for using our service. Goodbye!",
                'action': 'end_session'
            }

        # Map menu options to actions
        actions = {
            MenuOption.LOAN_STATEMENT: 'fetch_loan_statement',
            MenuOption.REPAYMENT_SCHEDULE: 'fetch_repayment_schedule',
            MenuOption.ACCOUNT_SUMMARY: 'fetch_account_summary',
            MenuOption.NOTIFICATIONS: 'fetch_notifications'
        }

        return {
            'message': f"Fetching your {option.name.lower().replace('_', ' ')}...",
            'action': actions.get(option)
        } 