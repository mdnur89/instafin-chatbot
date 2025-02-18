from .cache import set_user_state, get_user_state
from utils.insta_fin_api import ClientLookupAPIClient
from users.models import User

# Define states as constants
MAIN_MENU = "main_menu"
MY_ACCOUNT = "my_account"
FAQS = "faqs"
LIVE_AGENT = "live_agent"
REQUEST_ACCOUNT_NUMBER = "request_account_number"
VALIDATE_ACCOUNT_ID = "validate_account_id"
ACCOUNT_DETAILS_MENU = "account_details_menu"
LOAN_DETAILS = "loan_details"
REPAYMENT_SCHEDULES = "repayment_schedules"
ACCOUNT_SUMMARY = "account_summary"
RETURN_TO_MENU = "return_to_menu"

# Helper methods for state management
def set_state(user_id, state, timeout=300):
    """
    Set the user's current state in the cache.
    """
    set_user_state(user_id, state, timeout)


def get_state(user_id):
    """
    Get the user's current state from the cache.
    """
    return get_user_state(user_id)


# Main state handler
def handle_state(user_id, input_data):
    """
    Handle user interaction based on their current state.
    :param user_id: Unique identifier for the user
    :param input_data: User input (e.g., menu option or text)
    :return: A response dict with a message and optional menu
    """
    current_state = get_state(user_id)

    # State handling logic
    state_handlers = {
        MAIN_MENU: handle_main_menu,
        MY_ACCOUNT: handle_my_account,
        REQUEST_ACCOUNT_NUMBER: validate_account_id,
        VALIDATE_ACCOUNT_ID: validate_account_id,
        ACCOUNT_DETAILS_MENU: account_details_menu,
        LOAN_DETAILS: handle_loan_details,
        REPAYMENT_SCHEDULES: handle_repayment_schedules,
        ACCOUNT_SUMMARY: handle_account_summary,
        FAQS: handle_faqs,
        LIVE_AGENT: handle_live_agent,
    }

    # Default fallback if state is not found or invalid
    handler = state_handlers.get(current_state, handle_invalid_state)
    return handler(user_id, input_data)


# State-specific handlers
def handle_main_menu(user_id, option):
    """
    Handle the main menu state.
    """
    menu = ["1. My Account", "2. FAQs", "3. Live Agent"]

    if option == "1":
        return handle_my_account(user_id, None)
    elif option == "2":
        set_state(user_id, FAQS)
        return {"message": "You selected 'FAQs'. Here are some common questions and answers...", "menu": menu}
    elif option == "3":
        set_state(user_id, LIVE_AGENT)
        return {"message": "Connecting you to a live agent...", "menu": menu}
    else:
        return {"message": "Invalid option. Please choose 1, 2, or 3.", "menu": menu}


def handle_my_account(user_id, _):
    """
    Check if the user has an account ID and handle accordingly.
    """
    try:
        user = User.objects.get(username=user_id)
        if user.wisrod_account_id:
            # User has an account ID, proceed to the account details menu
            set_state(user_id, ACCOUNT_DETAILS_MENU)
            return {
                "message": "Welcome back! What would you like to do?",
                "menu": ["1. Loan Details", "2. Repayment Schedules", "3. Account Summary"],
            }
        else:
            # User does not have an account ID, ask for it
            set_state(user_id, REQUEST_ACCOUNT_NUMBER)
            return {"message": "Please provide your Account ID to proceed with get your account statement."}
    except User.DoesNotExist:
        return {"message": "User not found. Returning to the main menu.", "menu": ["1. My Account", "2. FAQs", "3. Live Agent"]}


def request_account_number(user_id, account_id):
    """
    Request the user to provide their account ID.
    """
    set_state(user_id, VALIDATE_ACCOUNT_ID)
    return {"message": f"Thanks! Verifying account ID `{account_id}`. Please wait..."}

def validate_account_id(user_id, account_id):
    """
    Validate the provided account ID via an API and save it if valid.
    """
    client = ClientLookupAPIClient.lookup_client(identifier=account_id, is_external_id=False)
    
    if client:  # Account ID is valid
        try:
            print(client)
            user = User.objects.get(username=user_id)
            user.wisrod_account_id = account_id

            # Save client details if they are not None
            if client.get("name"):
                user.first_name = client["name"]
            if client.get("email"):
                user.email = client["email"]
            if client.get("mobile"):
                user.phone_number = client["mobile"]

            user.save()
            set_state(user_id, ACCOUNT_DETAILS_MENU)
            return {
                "message": f"Hi {user.first_name}, What would you like to do next?",
                "menu": ["1. Loan Statements", "2. Repayment Schedules", "3. Account Summary"],
            }
        except User.DoesNotExist:
            return {"message": "User not found. Unable to link account ID. Returning to the main menu."}
    else:
        # Invalid account ID, ask the user to try again
        set_state(user_id, REQUEST_ACCOUNT_NUMBER)
        return {"message": f"The Account ID you have provided does not match any record with Wisrod Investment.\n\nKindly check and provide the account ID again"}



def account_details_menu(user_id, option):
    """
    Handle the account details menu.
    """
    if option == "1":
        set_state(user_id, LOAN_DETAILS)
        return handle_loan_details(user_id, None)
    elif option == "2":
        set_state(user_id, REPAYMENT_SCHEDULES)
        return handle_repayment_schedules(user_id, None)
    elif option == "3":
        set_state(user_id, ACCOUNT_SUMMARY)
        return handle_account_summary(user_id, None)
    else:
        return {
            "message": "Invalid option. Please choose 1, 2, or 3.",
            "menu": ["1. Loan Details", "2. Repayment Schedules", "3. Account Summary"],
        }


def handle_loan_details(user_id, _):
    """
    Handle the loan details state.
    """
    set_state(user_id, ACCOUNT_DETAILS_MENU)
    return {"message": "Here are your loan details...", "menu": ["1. Loan Details", "2. Repayment Schedules", "3. Account Summary"]}


def handle_repayment_schedules(user_id, _):
    """
    Handle the repayment schedules state.
    """
    set_state(user_id, ACCOUNT_DETAILS_MENU)
    return {"message": "Here is your repayment schedule...", "menu": ["1. Loan Details", "2. Repayment Schedules", "3. Account Summary"]}


def handle_account_summary(user_id, _):
    """
    Handle the account summary state.
    """
    set_state(user_id, ACCOUNT_DETAILS_MENU)
    return {"message": "Here is your account summary...", "menu": ["1. Loan Details", "2. Repayment Schedules", "3. Account Summary"]}


def handle_faqs(user_id, _):
    """
    Handle the FAQs state.
    """
    set_state(user_id, MAIN_MENU)
    return {
        "message": "Here are some FAQs:\n1. What services do you offer?\n2. How can I apply for a loan?\n3. What are your interest rates?\n\nReturning to the main menu.",
        "menu": ["1. My Account", "2. FAQs", "3. Live Agent"],
    }


def handle_live_agent(user_id, _):
    """
    Handle the Live Agent state.
    """
    set_state(user_id, MAIN_MENU)
    return {
        "message": "A live agent will connect with you shortly. Returning to the main menu.",
        "menu": ["1. My Account", "2. FAQs", "3. Live Agent"],
    }


def handle_invalid_state(user_id, _):
    """
    Handle invalid or unrecognized states.
    """
    set_state(user_id, MAIN_MENU)
    return {
        "message": "I didn't understand that. Returning to the main menu.",
        "menu": ["1. My Account", "2. FAQs", "3. Live Agent"],
    }