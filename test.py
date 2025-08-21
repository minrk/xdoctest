from __future__ import annotations

import asyncio
from contextvars import ContextVar


_loop: ContextVar[asyncio.AbstractEventLoop | None] = ContextVar("_loop", default=None)

def test_crash():
    local_loop = asyncio.new_event_loop()
    # _loop.set(asyncio.new_event_loop())

if __name__ == "__main__":
    test_crash()
    print("cleaning up")
