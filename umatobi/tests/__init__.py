# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import io, os, socket, threading, queue, random, pickle
from contextlib import contextmanager
from unittest.mock import patch
from datetime import timedelta
import functools

from umatobi.tests.constants import *
from umatobi.lib import *
from umatobi.lib.simulation_time import SimulationTime, PathMaker
from umatobi.simulator.node.core import NodeCore

SIMULATION_SECONDS = 30
D_TIMEDELTA = {
    "test_watson_start": \
        timedelta(0, SIMULATION_SECONDS - 1, 0),
    "test_elapsed_time": \
        timedelta(0, 73, 138770),
}
TD_ZERO = timedelta(0, 0, 0)

def replace_atat_n(new):
    return  TESTS_ATAT_N_YAML_PATH.replace(ATAT_N, new)

def make_node_core_assets(path_maker=None):
    byebye_nodes = threading.Event()
    if not path_maker:
        path_maker = PathMaker()
    _queue_darkness = queue.Queue()

    d = {
        'byebye_nodes': byebye_nodes,
        'path_maker': path_maker,
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

def make_growing_dicts(num_nodes, n_node_pickled, id_index):
    node_core_assets = make_node_core_assets()

    growing_dicts = [None] * n_node_pickled
    for i in range(n_node_pickled):
        node_core = NodeCore(host='localhost',
                      id=id_index + (i % num_nodes),
                       **node_core_assets)
        node_core.key.update()
        got_attrs = node_core.get_attrs()

        elapsed_time = random.randint(0, 100 ** 2 - 1)
        node_core_pickled = pickle.dumps(got_attrs)

        growing_dicts[i] = \
            make_growing_dict(None, elapsed_time, node_core_pickled)

    growing_dicts[0]['elapsed_time'] = growing_dicts[1]['elapsed_time']

    return growing_dicts
