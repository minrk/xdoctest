from jupyter_core.utils import run_sync


async def task():
    return

def test_xdoctest_debug():
    run_sync(task)()

if __name__ == "__main__":
    test_xdoctest_debug()
