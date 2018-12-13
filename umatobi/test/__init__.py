import datetime, io

from umatobi.constants import *
SIMULATION_DIR = 'umatobi-simulation-test'
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
