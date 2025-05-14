import random
import string

def generate_request_number():
    prefix = ''.join(random.choices(string.ascii_uppercase, k=2))
    number = ''.join(random.choices(string.digits, k=8))
    return prefix + number