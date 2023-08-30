__all__ = ['Task']

from typing import Coroutine
from .time import TimeoutHandler
from .excaptions import (
    CancelledError,
    TaskNotStartedError
)


def _create_task(coro: Coroutine):
    return Task(coro)


class Task(object):
    __slots__ = (
        '_coro',
        '_id',
        '_is_running',
        '_timeout_handler',
        '_cancel'
    )
    global_id = 0

    def __init__(self, coro: Coroutine):
        self._coro: Coroutine = coro
        self._id: int = Task.global_id
        self._timeout_handler = TimeoutHandler()
        self._is_running = False
        self._cancel = False

        Task.global_id += 1

    def cancel(self):
        if not self._is_running:
            raise TaskNotStartedError()

        self._is_running = False
        self._cancel = True

    def get_id(self) -> int:
        return self._id

    def get_coro(self) -> Coroutine:
        return self._coro

    def get_timeout_handler(self) -> TimeoutHandler:
        return self._timeout_handler

    def get_timeout(self):
        return self._timeout_handler.check()[1]

    def set_timeout(
            self,
            timeout: float
    ) -> None:
        self._timeout_handler.set_timeout(timeout)

    def next(self, data=None):
        if self._cancel:
            data = CancelledError(self)

        if not self._is_running:
            self._is_running = True

        return self._coro.send(data)

    def __repr__(self):
        return f'<aio.Task(id={self.get_id()})>'

    def __await__(self):
        raise NotImplementedError
