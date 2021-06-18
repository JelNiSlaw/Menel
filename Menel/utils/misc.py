import datetime
import random
import string
import time
from typing import Literal


def clamp(val: int, minval: int, maxval: int):
    return minval if val < minval else maxval if val > maxval else val


def chunk(iterator: list, max_size: int) -> list:
    for i in range(0, len(iterator), max_size):
        yield iterator[i:i + max_size]


def random_string(length: int = 16) -> str:
    return ''.join(random.choices(string.ascii_letters, k=length))


def unique_id() -> str:
    return hex(time.time_ns() + random.randrange(0, 100))[2:]


class DiscordTime:
    ALLOWED_FLAGS = ('t', 'T', 'd', 'D', 'f', 'F', 'R')

    def __init__(self, value: datetime.datetime):
        self._time = value

    def __format__(self, flag: Literal[ALLOWED_FLAGS]) -> str:
        if flag == '':
            return f'<t:{self._time.timestamp()}>'

        if flag not in {'t', 'T', 'd', 'D', 'f', 'F', 'R'}:
            raise ValueError(f'Invalid timestamp flag {flag!r}')

        return f'<t:{self._time.timestamp()}:{flag}>'