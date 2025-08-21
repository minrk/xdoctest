
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
    
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        inner = coro(*args, **kwargs)
        loop = ensure_event_loop()
        return loop.run_until_complete(inner)

    wrapped.__doc__ = coro.__doc__
    return wrapped


def ensure_event_loop() -> asyncio.AbstractEventLoop:
    # Get the loop for this thread, or create a new one.
    loop = _loop.get()
    if loop is not None and not loop.is_closed():
        return loop
    loop = asyncio.new_event_loop()
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
