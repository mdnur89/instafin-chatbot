from django.core.cache import cache

def set_user_state(user_id, state, timeout=300):
    """
    Set the user's current state in the cache.
    """
    cache.set(f"user_state_{user_id}", state, timeout)

def get_user_state(user_id):
    """
    Get the user's current state from the cache.
    """
    return cache.get(f"user_state_{user_id}")

def clear_user_state(user_id):
    """
    Clear the user's state from the cache.
    """
    cache.delete(f"user_state_{user_id}")