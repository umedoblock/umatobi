import io, os, socket, threading, queue
from contextlib import contextmanager
from unittest.mock import patch
from datetime import timedelta
import functools

from umatobi.tests.constants import *
from umatobi.lib import *

SIMULATION_SECONDS = 30
D_TIMEDELTA = {
    "test_watson_start": \
        timedelta(0, SIMULATION_SECONDS - 1, 0),
    "test_elapsed_time": \
        timedelta(0, 73, 138770),
}
TD_ZERO = timedelta(0, 0, 0)

def make_node_assets():
    byebye_nodes = threading.Event()
    iso8601 = SimulationTime().get_iso8601()
    _queue_darkness = queue.Queue()

    d = {
        'byebye_nodes': byebye_nodes,
        'iso8601': iso8601,
        '_queue_darkness': _queue_darkness,
    }

    return d

class MockIO(io.BytesIO):
    def recv(self, bufsize, flags=0):
        return self.read(bufsize)

@contextmanager
def recv_the_script_from_sock(speaking, bufsize=0):
    # He is such a ventriloquist.
    # This must be a feat of ventriloquism.
    with patch('umatobi.lib.sock_recv') as script:
        script.return_value = speaking

        try:
            yield
        finally:
            pass

@contextmanager
def time_machine(the_era):
    with patch.object(SimulationTime, 'now') as mocked_now:
        mocked_now.return_value = the_era

        try:
            yield
        finally:
            pass

def fixtures(f):
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        ret = f(self, *args, **kwargs)
        return ret
    return wrapper

# see decora_success.py
# def fixtures(*args, **kwargs):
#     logger.info(f'fixtures(args={args}, kwargs={kwargs})')
#     # __init__.py fixtures() - fixtures(args=('tests/fixtures/test.yaml',
#     #  'quentin'), kwargs={}) -...
#
#     def inner(self, func):
#         logger.info(f'func={func}')
#         return func(100)
#     return inner
