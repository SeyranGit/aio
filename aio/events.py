__all__ = [
    'BaseEventLoop',
    'AbstractEventLoop'
]

from typing import Coroutine
from .task import Task, _create_task
from .excaptions import (
    LoopNotStartedError,
    LoopAlreadyStartedError
)


class AbstractEventLoop(object):
    def get_tasks(self):
        """
        Returns created tasks.
        """
        raise NotImplementedError

    def get_loop(self):
        """
        Returns the loop object
        if it is running.
        """
        if self.is_running():
            return self

        raise LoopNotStartedError()

    def is_running(self) -> bool:
        """
        Returns information whether
        the loop is running.
        """
        raise NotImplementedError

    def is_closed(self):
        """
        Returns information whether
        the loop is closed.
        """
        raise NotImplementedError

    def run(self):
        """
        Starts the event loop.
        """
        raise NotImplementedError

    def close(self):
        """
        Ends the event loop.
        """
        raise NotImplementedError

    def __enter__(self):
        self.run()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close()


class BaseEventLoop(AbstractEventLoop):

    def __init__(self, coro: Coroutine | None = None) -> None:
        self._is_closed = True
        self._is_running = False
        self._tasks: list[Task] = []
        self._main_coro = coro
        self._current_task: Task | None = None

    def create_task(self, coro: Coroutine) -> Task:
        if isinstance(coro, Coroutine):
            task = _create_task(coro)
            return task

        raise ValueError(f'{coro} is not coroutine.')

    def append_task(self, task: Task) -> None:
        self._tasks.append(task)

    def get_maincoro(self) -> Coroutine:
        return self._main_coro

    def del_task(self, task: Task):
        self._tasks.remove(task)

    def get_tasks(self) -> list[Task]:
        return self._tasks

    def get_current_task(self) -> Task:
        return self._current_task

    def set_current_task(self, task: Task) -> None:
        self._current_task = task

    def is_running(self) -> bool:
        return self._is_running

    def is_closed(self) -> bool:
        return self._is_closed

    def close(self) -> None:
        if not self._is_closed:
            self._is_closed = True
            self.is_running = False

    def run(self, coro: Coroutine | None = None) -> None:
        if self._is_closed:
            self._is_running = True
            self._is_closed = False
            if coro:
                self._current_task = self.create_task(coro)
            elif self._main_coro:
                self._current_task = self.create_task(self._main_coro)
            else:
                raise ValueError(
                    'BaseEventLoop.run must take '
                    'a coroutine object'
                )
        else:
            raise LoopAlreadyStartedError()
