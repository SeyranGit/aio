__all__ = [
    'socket'
]

import socket as _socket
from . import io


def socket(*args, **kwargs):
    return io.Socket(_socket.socket(*args, **kwargs))
