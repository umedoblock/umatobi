# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

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

def make_node_assets(start_up_orig=None):
    byebye_nodes = threading.Event()
    if not start_up_orig:
        start_up_orig = SimulationTime()
    _queue_darkness = queue.Queue()

    d = {
        'byebye_nodes': byebye_nodes,
        'start_up_orig': start_up_orig,
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
