import asyncio
import os
import threading
from pathlib import Path
import zmq


def test_xdoctest_debug():

    with zmq.Context() as ctx:
        interface = "tcp://127.0.0.1"
        with ctx.socket(zmq.ROUTER) as server, ctx.socket(zmq.DEALER) as client:
            server.linger = client.linger = 1_000
            port = server.bind_to_random_port(interface)
            url = f"{interface}:{port}"
            client.connect(url)
            client.send(b"ping")
            msg = server.recv_multipart()
            server.send_multipart(msg)
            reply = client.recv_multipart()

    # import nbformat  # NOQA
    # from nbclient import NotebookClient
    from jupyter_core.utils import run_sync

    if "REPO_ROOT" in os.environ:
        root_dir = Path(os.environ["REPO_ROOT"])
    else:
        root_dir = Path(__file__).parent
    root_dir = root_dir.resolve()

    # notebook_fpath = root_dir / "tests" / "notebook_with_doctests.ipynb"
    # with open(notebook_fpath, "r+") as file:
        # nb = nbformat.read(file, as_version=nbformat.NO_CONVERT)
    # print("creating client")
    # nbc = NotebookClient(nb)
    # print("executing")
    # ctx = zmq.Context.instance()
    # print(f"before {ctx._sockets=}")
    from jupyter_client import KernelManager, AsyncKernelManager
    from functools import partial
    async def f():
        km = AsyncKernelManager()
        print(f"{km=}")
        run_sync(km.start_kernel)()
        print(f"{km.context=}")
            # kc = km.client()
            # print(f"{kc=}")
            # kc.start_channels()
            # await kc.wait_for_ready()
            # kc.stop_channels()
            # kc.context.destroy()
        run_sync(km.shutdown_kernel)(now=True)
        print(f"{km.context=}")
        run_sync(km.cleanup_resources)()
            # print(f"{kc.context=}")
        print(f"{km.context=}")
            # km.context.destroy()
        print(f"{threading.enumerate()=}")
    asyncio.run(f())
    
    # run_sync(km.)
    # with nbc.setup_kernel():
    #     print(f"during {ctx._sockets=}")
    #     kc_ctx = nbc.kc.context
    #     km_ctx = nbc.km.context
    #     print(f"{ctx=} {km_ctx=} {kc_ctx=}")
# 
    # print(f"{ctx=} {km_ctx=} {kc_ctx=}")
    # print("destroying kc")
    # km_ctx.destroy()
    # print("destroyed kc")
    # nb = nbc.execute()
    # print("executed")
    # for cell in nb.cells:
    #     if cell.cell_type == "code":
    #         for output in cell.outputs:
    #             if output.output_type == "stream":
    #                 print(output.text)
    print(f"after {ctx._sockets=}")
    ctx.destroy()
    print("destroyed")

if __name__ == "__main__":
    test_xdoctest_debug()
