from types import coroutine
from .requests import (
    _WAIT_SOCK_ACCEPT,
    _WAIT_SOCK_WRITE,
    _WAIT_SOCK_READ
)


@coroutine
def _to_kernel(request, *args):
    """
    The same function that transfers
    control to the event loop using
    the yield operator.
    """
    response = yield request, *args
    if isinstance(response, BaseException):
        raise response

    return response


async def _wait_sock_read(*args):
    return await _to_kernel(_WAIT_SOCK_READ, *args)


async def _wait_sock_write(*args):
    return await _to_kernel(_WAIT_SOCK_WRITE, *args)


async def _wait_sock_accept(*args):
    return await _to_kernel(_WAIT_SOCK_ACCEPT, *args)
