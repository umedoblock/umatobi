import datetime, io, os
from contextlib import contextmanager
from unittest.mock import patch

from umatobi.constants import *
SIMULATION_DIR = os.path.join(__name__.split('.')[1], 'umatobi-simulation')
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')

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
def time_machine(the_era):
    with patch('umatobi.lib.datetime_now') as mocked_Foo:
        mocked_Foo.return_value = the_era

        try:
            yield
        finally:
            pass
