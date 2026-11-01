# -- Controls the current user of the application when executed. --

# Store the currently logged-in user's information
_current_user = None


def set_user(user):
    """user = {"account_number": ..., "account_name": ..., "identifier": ...}"""
    # Save a copy of the logged-in user's information
    global _current_user
    _current_user = dict(user)


def get_user():
    # Return a copy of the current user's information
    return dict(_current_user) if _current_user else None


def clear_user():
    # Remove the current user's session information during logout
    global _current_user
    _current_user = None
