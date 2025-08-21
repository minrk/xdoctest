
# jupyter_core.utils.run_sync from jupyter_core

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from __future__ import annotations

import asyncio
import atexit
import errno
import inspect
import sys
import threading
from contextvars import ContextVar
from typing import Any, Awaitable, Callable, TypeVar, cast


T = TypeVar("T")


class _TaskRunner:
    """A task runner that runs an asyncio event loop on a background thread."""

    def __init__(self) -> None:
        self.__io_loop: asyncio.AbstractEventLoop | None = None
        self.__runner_thread: threading.Thread | None = None
        self.__lock = threading.Lock()
        atexit.register(self._close)

    def _close(self) -> None:
        print("in self._close", self, self.__io_loop)
        if self.__io_loop:
            self.__io_loop.stop()
        print("runner closed")

    def _runner(self) -> None:
        loop = self.__io_loop
        assert loop is not None
        try:
            loop.run_forever()
        finally:
            loop.close()

    def run(self, coro: Any) -> Any:
        """Synchronously run a coroutine on a background thread."""
        with self.__lock:
            name = f"{threading.current_thread().name} - runner"
            if self.__io_loop is None:
                self.__io_loop = asyncio.new_event_loop()
                self.__runner_thread = threading.Thread(target=self._runner, daemon=True, name=name)
                self.__runner_thread.start()
        fut = asyncio.run_coroutine_threadsafe(coro, self.__io_loop)
        return fut.result(None)


_runner_map: dict[str, _TaskRunner] = {}
_loop: ContextVar[asyncio.AbstractEventLoop | None] = ContextVar("_loop", default=None)


def run_sync(coro: Callable[..., Awaitable[T]]) -> Callable[..., T]:
    """Wraps coroutine in a function that blocks until it has executed.

    Parameters
    ----------
    coro : coroutine-function
        The coroutine-function to be executed.

    Returns
    -------
    result :
        Whatever the coroutine-function returns.
    """

    assert inspect.iscoroutinefunction(coro)

    def wrapped(*args: Any, **kwargs: Any) -> Any:
        name = threading.current_thread().name
        inner = coro(*args, **kwargs)
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            # No loop running, run the loop for this thread.
            loop = ensure_event_loop()
            return loop.run_until_complete(inner)

        # Loop is currently running in this thread,
        # use a task runner.
        if name not in _runner_map:
            _runner_map[name] = _TaskRunner()
        return _runner_map[name].run(inner)

    wrapped.__doc__ = coro.__doc__
    return wrapped


def ensure_event_loop(prefer_selector_loop: bool = False) -> asyncio.AbstractEventLoop:
    # Get the loop for this thread, or create a new one.
    loop = _loop.get()
    if loop is not None and not loop.is_closed():
        return loop
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        if sys.platform == "win32" and prefer_selector_loop:
            loop = asyncio.WindowsSelectorEventLoopPolicy().new_event_loop()
        else:
            loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    _loop.set(loop)
    return loop


async def task():
    print("in test")
    return

def test_crash():
    run_sync(task)()
    print("test done")

if __name__ == "__main__":
    test_crash()
    print("cleaning up")
