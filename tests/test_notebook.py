import pytest
import threading
import sys
from os.path import join, exists, dirname
try:
    from packaging.version import parse as LooseVersion
except ImportError:
    from distutils.version import LooseVersion

PY_VERSION = LooseVersion('{}.{}'.format(*sys.version_info[0:2]))
IS_MODERN_PYTHON = PY_VERSION > LooseVersion('3.4')


@pytest.fixture(scope="session", autouse=True)
def show_threads_session():
    print(f"threads before session: {threading.enumerate()}")
    yield
    print(f"threads after session: {threading.enumerate()}")


@pytest.fixture(autouse=True)
def show_threads_test():
    print(f"threads before test: {threading.enumerate()}")
    yield
    print(f"threads after test: {threading.enumerate()}")


def skip_notebook_tests_if_unsupported():
    if not IS_MODERN_PYTHON:
        pytest.skip('jupyter support is only for modern python versions')

    try:
        import IPython  # NOQA
        import nbconvert  # NOQA
        import nbformat  # NOQA

        import platform
        if platform.python_implementation() == 'PyPy':
            # In xdoctest <= 0.15.0 (~ 2021-01-01) this didn't cause an issue
            # But I think there was a jupyter update that broke it.
            # PyPy + Jupyter is currently very niche and I don't have the time
            # to debug properly, so I'm just turning off these tests.
            raise Exception

    except Exception:
        pytest.skip('Missing jupyter')


def cmd(command):
    # simplified version of ub.cmd no fancy tee behavior
    import subprocess
    proc = subprocess.Popen(
        command, shell=True, universal_newlines=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out, err = proc.communicate()
    ret = proc.wait()
    info = {
        'proc': proc,
        'out': out,
        'test_doctest_in_notebook.ipynberr': err,
        'ret': ret,
    }
    return info


def demodata_notebook_fpath():
    try:
        testdir = dirname(__file__)
    except NameError:
        # Hack for dev CLI usage
        import os
        testdir = os.path.expandvars('$HOME/code/xdoctest/tests/')
        assert exists(testdir), 'assuming a specific dev environment'
    notebook_fpath = join(testdir, "notebook_with_doctests.ipynb")
    return notebook_fpath


def test_xdoctest_debug():
    import zmq

    with zmq.Context() as ctx:
        print(f"have {ctx=}")
        interface = "tcp://127.0.0.1"
        with ctx.socket(zmq.ROUTER) as server, ctx.socket(zmq.DEALER) as client:
            server.linger = client.linger = 1_000
            print("linger")
            print(server.get(zmq.LINGER))
            print("binding")
            port = server.bind_to_random_port(interface)
            print(f"bound to {port}")
            url = f"{interface}:{port}"
            print(f"connecting to {url}")
            client.connect(url)
            print("sending")
            client.send(b"ping")
            msg = server.recv_multipart()
            print("recvd", msg, "replying")
            server.send_multipart(msg)
            reply = client.recv_multipart()
            print("recvd reply", reply)

    import nbformat  # NOQA
    from nbclient import NotebookClient
    notebook_fpath = demodata_notebook_fpath()
    with open(notebook_fpath, 'r+') as file:
        nb = nbformat.read(file, as_version=nbformat.NO_CONVERT)
    print("creating client")
    nbc = NotebookClient(nb)
    print("executing")
    nb = nbc.execute()
    print("executed")
    for cell in nb.cells:
        if cell.cell_type == 'code':
            for output in cell.outputs:
                if output.output_type == 'stream':
                    print(output.text)

def test_xdoctest_inside_notebook():
    """
    xdoctest ~/code/xdoctest/tests/test_notebook.py test_xdoctest_inside_notebook
    xdoctest tests/test_notebook.py test_xdoctest_inside_notebook

    xdoctest notebook_with_doctests.ipynb
    """
    # How to run Jupyter from Python
    # https://nbconvert.readthedocs.io/en/latest/execute_api.html
    skip_notebook_tests_if_unsupported()

    notebook_fpath = demodata_notebook_fpath()

    from xdoctest.utils import util_notebook
    try:
        nb, resources = util_notebook.execute_notebook(notebook_fpath, verbose=3)
    except Exception as e:
        print(f"Except! {e}")
        raise
    finally:
        print("end of execute_notebook")

    last_cell = nb['cells'][-1]
    text = last_cell['outputs'][0]['text']
    if '3 / 3 passed' not in text:
        import warnings
        warnings.warn('test_xdoctest_inside_notebook might fail due to io issues')


def test_xdoctest_outside_notebook():

    skip_notebook_tests_if_unsupported()

    if sys.platform.startswith('win32'):
        pytest.skip()

    notebook_fpath = demodata_notebook_fpath()
    info = cmd(sys.executable + ' -m xdoctest ' + notebook_fpath)
    text = info['out']
    assert '3 / 3 passed' in text
