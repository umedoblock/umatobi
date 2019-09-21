import io, os, socket
from contextlib import contextmanager
from unittest.mock import patch
from datetime import timedelta

from umatobi.tests.constants import *
from umatobi.lib import SimulationTime

SIMULATION_SECONDS = 30
D_TIMEDELTA = {
    "test_watson_start": \
        timedelta(0, SIMULATION_SECONDS - 1, 0),
    "test_elapsed_time": \
        timedelta(0, 73, 138770),
}
TD_ZERO = timedelta(0, 0, 0)

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
