from __future__ import annotations

import asyncio
from contextvars import ContextVar


context_loop: ContextVar[asyncio.AbstractEventLoop | None] = ContextVar("context_loop", default=None)

def test_crash():
    loop = asyncio.new_event_loop()
    context_loop.set(loop)
    # if loop is unclosed, Windows Python 3.14rc2 segfaults at exit
    # loop.close()

if __name__ == "__main__":
    test_crash()
    print("cleaning up")
