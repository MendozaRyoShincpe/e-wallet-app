# -- Controls the current user of the application when executed. --

_current_user = None


def set_user(user):
    """user = {"account_number": ..., "account_name": ..., "identifier": ...}"""
    global _current_user
    _current_user = dict(user)


def get_user():
    return dict(_current_user) if _current_user else None


def clear_user():
    global _current_user
    _current_user = None