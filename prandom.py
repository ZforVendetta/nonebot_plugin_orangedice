import secrets

def random(min_value, max_value):
    return secrets.randbelow(max_value - min_value + 1) + min_value