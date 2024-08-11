from funcy import get_in


def safe_get_in(dictionary, path, default=None):
    try:
        return get_in(dictionary, path, default)
    except Exception as e:
        return None
