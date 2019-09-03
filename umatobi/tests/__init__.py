import datetime, io, os, socket
from contextlib import contextmanager
from unittest.mock import patch

from umatobi import constants

constants.SIMULATION_DIR = os.path.join(os.path.dirname(__file__), 'umatobi-simulation')
constants.FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')
constants.LOGGER_STREAM = open(os.path.join(constants.SIMULATION_DIR, 'stdout.log'), 'w')

from umatobi.constants import *

SIMULATION_SECONDS = 30
D_TIMEDELTA = {
    "test_watson_start": \
        datetime.timedelta(0, SIMULATION_SECONDS - 1, 0),
    "test_elapsed_time": \
        datetime.timedelta(0, 73, 138770),
}
TD_ZERO = datetime.timedelta(0, 0, 0)

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
    with patch('umatobi.lib.datetime_now') as mocked_Foo:
        mocked_Foo.return_value = the_era

        try:
            yield
        finally:
            pass
