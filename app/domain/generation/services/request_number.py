import random
import string

def generate_request_number():
    return "".join(random.choices(string.ascii_letters + string.digits, k=8))