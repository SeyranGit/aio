__all__ = [
    'Kernel',
    'run',
    'to_plan',
    'get_loop',
    'get_kernel',
    'kernel_init',
    'is_task',
    'is_coroutine'
]

import time
import types

from typing import (
    Coroutine,
    Any,
    NoReturn
)

from .task import Task
from .events import BaseEventLoop
from .excaptions import (
    LoopNotStartedError,
    KernelNotInitializedError,
    TerminatedEventLoop
)
from .requests import (
    _SLEEP,
    _WAIT_SOCK_WRITE,
    _WAIT_SOCK_READ,
    _WAIT_SOCK_ACCEPT,
)


class Kernel(object):
    def __init__(self, loop: BaseEventLoop | None = None) -> None:
        self._eventloop: BaseEventLoop | None = loop

    def request(self, request, *args) -> None:
        loop = self.get_loop()
        task = loop.get_current_task()
        if request == _SLEEP:
            task.set_timeout(args[0])

        if request in (
                _WAIT_SOCK_ACCEPT,
                _WAIT_SOCK_WRITE,
                _WAIT_SOCK_READ
        ):
            task.set_timeout(0.05)

    def get_loop(self) -> BaseEventLoop:
        if self._eventloop:
            return self._eventloop

        raise LoopNotStartedError()

    def to_plan(self, obj: Coroutine | Task) -> Task:
        loop = self.get_loop()
        if is_task(obj):
            loop.append_task(obj)
            return obj

        if is_coroutine(obj):
            task = loop.create_task(obj)
            loop.append_task(task)
            return task

        raise ValueError(f'{obj} is not coroutine.')

    def run(self, coro: Coroutine | None = None) -> Any:
        """
        Сreates and starts an event
        loop and processes the created tasks.
        """
        result = None
        loop = self._eventloop
        if not loop:
            if not coro:
                raise ValueError(
                    'The Kernel.run method needs to '
                    'pass the coroutine object.'
                )

            loop = self._eventloop = BaseEventLoop(coro)

        if not loop.get_maincoro():
            loop._main_coro = coro

        with loop as loop:
            self.to_plan(loop.get_maincoro())
            while not loop.is_closed():
                tasks: list[Task] = loop.get_tasks()
                try:
                    _tasks_handler(self, tasks)
                except TerminatedEventLoop as exc:
                    return exc.value


_kernel: Kernel | None = None


def _tasks_handler(kernel: Kernel, tasks: list[Task]) -> NoReturn:
    loop = kernel.get_loop()
    result = None
    for task in tasks:
        timeout_handler = task.get_timeout_handler()
        is_timeup, timeout = timeout_handler.check()
        if is_timeup:
            try:
                loop.set_current_task(task)
                result = task.next()
                kernel.request(*result)

            except StopIteration as exc:
                loop.del_task(task)
                if task.get_coro() == loop.get_maincoro():
                    raise TerminatedEventLoop(exc.value)
    else:
        try:
            timeout = min(
                task.get_timeout()
                for task in loop.get_tasks()
            )
            if timeout > time.time():
                time.sleep(timeout - time.time())
        except ValueError:
            raise TerminatedEventLoop(result)


def is_task(obj: Any) -> bool:
    return isinstance(obj, Task)


def is_coroutine(obj: Any) -> bool:
    return isinstance(obj, Coroutine)


def kernel_init(loop: BaseEventLoop):
    global _kernel
    _kernel = Kernel(loop)

    return _kernel


def get_loop() -> BaseEventLoop:
    """
    Returns the event loop object if it is running!
    If the kernel is not created,
    a <KernelNotInitializedError> exception is thrown.
    If the event loop is not running,
    a <LoopNotStartedError> exception is raised.
    """
    if _kernel:
        loop = _kernel.get_loop()
        if loop.is_running():
            return loop

        raise LoopNotStartedError()
    raise KernelNotInitializedError()


def get_kernel() -> Kernel | NoReturn:
    """
    Returns a Kernel object if it is created
    otherwise a <KernelNotInitializedError> exception is thrown.
    """
    if _kernel:
        return _kernel

    raise KernelNotInitializedError()


def to_plan(obj: Coroutine | Task):
    """
    Calls Kernel.to_plan with argument <obj>
    he in turn creates a task as needed
    and plans to implement it.
    """
    if _kernel:
        return _kernel.to_plan(obj)

    raise KernelNotInitializedError()


def run(coro: Coroutine) -> Any:
    """
    Сreates a kernel object and
    starts it with the coro argument,
    which in turn creates and starts the event loop.
    """
    global _kernel
    if is_coroutine(coro):
        _kernel = Kernel()
        return _kernel.run(coro)

    raise ValueError(f'{coro} is not coroutine.')
