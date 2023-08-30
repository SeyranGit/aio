__all__ = [
    'LoopNotStartedError',
    'KernelNotInitializedError',
    'TerminatedEventLoop',
    'LoopAlreadyStartedError',
    'CancelledError',
    'TaskNotStartedError'
]


class LoopAlreadyStartedError(Exception):
    def __str__(self):
        return 'Loop already started!'


class LoopNotStartedError(Exception):
    def __str__(self):
        return 'Loop not started!'


class KernelNotInitializedError(Exception):
    def __str__(self):
        return 'Kernel not initialized!'


class TerminatedEventLoop(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return 'Event loop terminated.'


class CancelledError(Exception):
    def __init__(self, task):
        self.task = task

    def __str__(self):
        return f'The task {self.task} was forcibly stopped.'


class TaskNotStartedError(Exception):
    def __str__(self):
        return 'Task not started.'
