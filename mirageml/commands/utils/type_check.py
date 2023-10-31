def is_convertable_to_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False
