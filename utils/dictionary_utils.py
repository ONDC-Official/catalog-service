from funcy import get_in


def safe_get_in(dictionary, path, default=None):
    try:
        return get_in(dictionary, path, default)
    except Exception as e:
        return None

def safe_int_parse(value, default=None):
    try:
        return int(value)
    except Exception as e:
        return default