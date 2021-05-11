import random
import string


def clamp(val, minval, maxval):
    return minval if val < minval else maxval if val > maxval else val


def random_string(length: int) -> str:
    return ''.join(random.choices(string.ascii_letters, k=length))