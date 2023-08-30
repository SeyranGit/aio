__all__ = [
    'TimeoutHandler',
    'sleep',
]

import time

from typing import Callable
from .requests import _SLEEP
from .kreq import _to_kernel


async def sleep(secnds: int) -> None:
    return await _to_kernel(_SLEEP, secnds)


class TimeoutHandler(object):
    __slots__ = (
        '_timeout',
        '_callback',
        '_args',
        '_kwargs'
    )

    def __init__(
            self,
            timeout: float = 0.0,
            callback: Callable | None = None,
            *args, **kwargs
    ) -> None:
        self._timeout = time.time() + timeout
        self._callback = callback
        self._args = args
        self._kwargs = kwargs

    def set_timeout(self, timeout):
        self._timeout = time.time() + timeout

    def get_timeout(self):
        return self._timeout

    def check(self):
        if time.time() >= self._timeout:
            if self._callback:
                self._callback(*self._args, **self._kwargs)

            return True, time.time()
        return False, self._timeout

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _time = self._timeout - time.time()
        if _time > 0:
            time.sleep(_time)
