from users.models import User
from .states import handle_state, MAIN_MENU, set_state


def handle_user_interaction(user_id, message_text):
    """
    Handle user interaction based on whether it's their first time or not.
    """
    try:
        user = User.objects.get(username=user_id)
        return existing_user_menu(user_id, message_text)
    except User.DoesNotExist:
        # If the user doesn't exist, create and welcome them
        user = User.objects.create(
            username=user_id
        )
        set_state(user_id, MAIN_MENU)
        return new_user_greeting(user_id, message_text)


def new_user_greeting(user_id, message_text):
    """
    Greet new user and show the menu.
    """
    return {
        "message": (
            "Welcome to **Wisrod Investments**! 👋\n\n"
            "Thanks for chatting with me. I am Wisrod Investment's 24/7 banking assistant. "
            "I can help you with:\n"
            "✅ Managing your account\n"
            "✅ Providing feedback\n"
            "✅ Reporting any issues\n\n"
            "**Need to cancel a transaction?** Simply type **'Cancel'** at any time.\n\n"
            "By continuing to use this chat service, you agree to be bound by our [Terms and Conditions](https://wisrod.com/disclaimer/).\n\n"
            "Please choose an option below: "
        ),
        "menu": [
            "1️⃣ My Account",
            "2️⃣ View FAQs",
            "3️⃣ Chat with an Agent"
        ]
    }


def existing_user_menu(user_id, message_text):
    """
    Show menu for existing users.
    """
    return handle_state(user_id, message_text)