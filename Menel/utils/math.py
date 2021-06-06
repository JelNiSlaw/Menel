import random
import string
import time


def clamp(val, minval, maxval):
    return minval if val < minval else maxval if val > maxval else val


def random_string(length: int = 16) -> str:
    return ''.join(random.choices(string.ascii_letters, k=length))


def unique_id() -> str:
    return hex(time.time_ns() + random.randrange(0, 100))[2:]