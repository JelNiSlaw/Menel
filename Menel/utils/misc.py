import time
from typing import Iterable, Optional, Union


def clamp(val: int, minval: int, maxval: int):
    return minval if val < minval else maxval if val > maxval else val


def chunk(iterator: Union[list, str], max_size: int) -> Iterable:
    for i in range(0, len(iterator), max_size):
        yield iterator[i:i + max_size]


class Timer:
    def __init__(self):
        self.time: Optional[float] = None

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, *_):
        self.time = time.perf_counter() - self._start