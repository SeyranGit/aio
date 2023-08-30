__all__ = [
    'Socket',
    'StreamBase',
    'StreamSocket'
]

import socket

from contextlib import contextmanager
from .requests import _WAIT_SOCK_WRITE
from .kreq import (
    _wait_sock_accept,
    _wait_sock_read,
    _wait_sock_write
)


class Socket(object):
    __slots__ = (
        '_socket',
        '_wait_connection'
    )

    def __init__(self, sock: socket.socket):
        self._socket: socket.socket = sock
        self._socket.setblocking(False)
        self._wait_connection = True

    def as_stream(self):
        return StreamSocket(self)

    def __getattr__(self, attr):
        return getattr(self._socket, attr)

    def __repr__(self):
        return (
            f'<aio.Socket(fd={self._socket.fileno()}, '
            f'family={self._socket.family}, '
            f'type={self._socket.type}, '
            f'proto={self._socket.proto}, '
            f'laddr={self._socket.getsockname()}>'
        )

    async def recv(self, maxsize: int = 1024) -> bytes:
        while True:
            try:
                return self._socket.recv(maxsize)
            except BlockingIOError:
                await _wait_sock_read()

    async def send(self, data: bytes = b''):
        while True:
            try:
                return self._socket.send(data)
            except BlockingIOError:
                await _wait_sock_write()

    async def accept(self):
        while True:
            try:
                client, addr = self._socket.accept()
                return type(self)(client), addr
            except BlockingIOError:
                await _wait_sock_accept()

    @contextmanager
    def blocking(self):
        self._socket.setblocking(True)
        yield self._socket
        self._socket.setblocking(False)

    async def hand(self):
        while True:
            try:
                return self._socket.do_handshake()
            except BlockingIOError:
                await _wait_sock_write()

    async def connect(self, address):
        with self.blocking():
            return self._socket.connect(address)

    async def __aenter__(self):
        self.socket.__enter__()
        return self

    async def __aexit__(self, *args):
        if self._socket:
            self._socket.__exit__(*args)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self._socket:
            self._socket.__exit__(*args)


class StreamBase(object):
    def __init__(self, fileobj):
        self._file = fileobj
        self._buffer = bytearray()

    async def readlines(self):
        data = await self.read()
        while data:
            nl = data.find(b'\n')
            yield data[:nl]
            if nl == -1:
                break

            data = data[nl + 1:]

    async def flush(self):
        await self.write(self._buffer)
        self._buffer.clear()

    async def readline(self):
        if not self._buffer:
            self._buffer.extend(await self.read())

        nl = self._buffer.find(b'\n')
        if nl >= 0:
            line = bytes(self._buffer[:nl + 1])
            del self._buffer[:nl + 1]

            return line

        else:
            line = bytes(self._buffer)
            self._buffer.clear()
            return line

    async def _read(self):
        raise NotImplementedError

    async def write(self, data: bytes) -> None:
        raise NotImplementedError

    async def read(self, length: int = -1) -> bytes:
        if self._buffer:
            if length == -1 or len(self._buffer) < length:
                data = bytes(self._buffer)
                self._buffer.clear()
            else:
                data = bytes(self._buffer[:length])
                del self._buffer[:length]
        else:
            data = await self._read()

        return data

    def __aiter__(self):
        return self

    async def __anext__(self):
        line = await self.readline()
        if line:
            return line
        else:
            raise StopAsyncIteration


class StreamSocket(StreamBase):
    async def _read(self, bytes_count: int = 1024):
        return await self._file.recv(bytes_count)

    async def write(self, data: bytes):
        return await self._file.send(data)
