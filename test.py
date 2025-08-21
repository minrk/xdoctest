import asyncio
from contextvars import ContextVar


context_loop = ContextVar("context_loop", default=None)

def test_crash():
    loop = asyncio.new_event_loop()
    context_loop.set(loop)
    # if loop is unclosed, Windows Python 3.14.0rc2 segfaults at exit
    # loop.close()

if __name__ == "__main__":
    test_crash()
    print("end of script")
