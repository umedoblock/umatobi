# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import threading, datetime, queue, pickle
import unittest
from unittest.mock import patch

from umatobi.tests.constants import *
from umatobi.tests import *
from umatobi.tests.helper import assert_queue
from umatobi.simulator.node.core import NodeCore
from umatobi.lib.simulation_time import SimulationTime

class NodeCoreTests(unittest.TestCase):

    def setUp(self):
        id_ = 100
        break_simulation = threading.Event()
        waked_up = threading.Event()
        queue_to_darkness = queue.Queue()

        self.node_core = \
            NodeCore(id_, break_simulation, waked_up, queue_to_darkness)

    def test_TO_DARKNESS(self):
        self.assertSetEqual(NodeCore.TO_DARKNESS, {'id', 'count'})

    @patch('umatobi.simulator.node.core.threading.Thread.__init__')
    def test___init__(self, mock_Thread):
        id_ = 100
        break_simulation = threading.Event()
        waked_up = threading.Event()
        queue_to_darkness = queue.Queue()

        with self.assertLogs('umatobi', level='INFO') as cm:
            node_core = NodeCore(id_, break_simulation, waked_up, queue_to_darkness)

        self.assertEqual(cm.output[0],
                       f'INFO:umatobi:NodeCore(id_={id_}) is created.')
        mock_Thread.assert_called_once_with(node_core)
        self.assertEqual(node_core.id, id_)
        self.assertEqual(node_core.break_simulation, break_simulation)
        self.assertFalse(node_core.break_simulation.is_set())
        self.assertEqual(node_core.waked_up, waked_up)
        self.assertFalse(node_core.waked_up.is_set())
        self.assertEqual(node_core.queue_to_darkness, queue_to_darkness)
        self.assertEqual(node_core.queue_to_darkness.qsize(), 0)

        self.assertEqual(node_core.count, 0)

        self.assertEqual(cm.output[1],
                       f'INFO:umatobi:NodeCore(id_={id_}) done.')

    def test_get_attrs(self):
        node_core = self.node_core

        self.assertEqual(node_core.get_attrs(), {'id', 'count'})

    def test_get_attrs_by_attrs(self):
        node_core = self.node_core

        attrs = ('a', 'b', 'c', 'd')
        self.assertEqual(node_core.get_attrs(attrs), set(attrs))

    def test_load_queue_by_attrs(self):
        expected_now = datetime.datetime(2019, 12, 12, 12, 12, 12, 121212)

        node_core = self.node_core

        expected_info = {
            'id': node_core.id,
            'count': node_core.count,
        }

        self.assertEqual(node_core.queue_to_darkness.qsize(), 0)
        with time_machine(expected_now):
            bytes_as_queue = \
                node_core.load_queue_by_attrs(node_core.get_attrs())
        self.assertIsInstance(bytes_as_queue, bytes)
        self.assertEqual(node_core.queue_to_darkness.qsize(), 1)

        got_queue = node_core.queue_to_darkness.get()
        self.assertEqual(node_core.queue_to_darkness.qsize(), 0)

        assert_queue(self, got_queue, expected_now, expected_info)

    # see above in detail
    # ClientTests.test_start() in tests/unit/test_client.py
    @patch.object(NodeCore, 'get_attrs', return_value=NodeCore.TO_DARKNESS,
                  autospec=True)
    @patch.object(NodeCore, 'load_queue_by_attrs', autospec=True)
    def test_run(self, *mocks):
        node_core = self.node_core

        # no call
        for mock in reversed(mocks):
            mn = mock.__name__
            try:
                mock.assert_called_once_with(node_core)
            except AssertionError as err:
                err_msg = f"Expected '{mn}' to be called once. Called 0 times."
                self.assertEqual(err.args[0], err_msg)
            self.assertEqual(0, mock.call_count)

        self.assertFalse(node_core.waked_up.is_set())
        with self.assertLogs('umatobi', level='INFO') as cm:
            with patch.object(node_core.break_simulation, 'wait') as mock_wait:
                node_core.run()

        self.assertTrue(node_core.waked_up.is_set())

        self.assertEqual(cm.output[0],
                       f'INFO:umatobi:{node_core} waked up.')

        # mocks[1].__name__ == 'get_attrs':
        mocks[1].assert_called_once_with(node_core)

        # mocks[0].__name__ == 'load_queue_by_attrs':
        mocks[0].assert_called_once_with(node_core, NodeCore.TO_DARKNESS)

        mock_wait.assert_called_once()

        self.assertEqual(cm.output[1],
                       f'INFO:umatobi:{node_core}.run() done.')

    def test_appear_by_instance(self):
        node_core = self.node_core

        with self.assertLogs('umatobi', level='INFO') as cm:
            with patch.object(node_core, 'start') as mock_start:
                node_core.appear()

        self.assertEqual(cm.output[0],
                       f'INFO:umatobi:{node_core}.appear().')
        mock_start.assert_called_once()
        self.assertEqual(cm.output[1],
                       f'INFO:umatobi:{node_core}.appear() done.')

    def test_appear(self):
        # I wrote too much and deeply test in detail.
        # I overwrite test in detail.

        node_core = self.node_core
        expected_info = {
            'id': node_core.id,
            'count': node_core.count,
        }
        expected_now = datetime.datetime(2019, 2, 19, 20, 19, 20, 192019)

        self.assertFalse(node_core.waked_up.is_set())

        self.assertEqual(node_core.queue_to_darkness.qsize(), 0)
        with self.assertLogs('umatobi', level='INFO') as cm:
            with patch.object(node_core.break_simulation, 'wait') as mock_wait:
                with time_machine(expected_now):
                    node_core.appear()
        self.assertEqual(node_core.queue_to_darkness.qsize(), 1)

        self.assertEqual(cm.output[0],
                       f'INFO:umatobi:{node_core}.appear().')

        # call automatically node_core.start() and run()
        self.assertTrue(node_core.waked_up.is_set())
        self.assertEqual(cm.output[1],
                       f'INFO:umatobi:{node_core} waked up.')

        # call automatically node_core.load_queue_by_attrs() in run()
        # stole loaded queue
        stole_queue = node_core.queue_to_darkness.get()
        # put it back in secret
        node_core.queue_to_darkness.put(stole_queue)

        assert_queue(self, stole_queue, expected_now, expected_info)

        mock_wait.assert_called_once()

        self.assertEqual(cm.output[2],
                       f'INFO:umatobi:{node_core}.run() done.')
        # finish to call node_core.run()

        self.assertEqual(cm.output[3],
                       f'INFO:umatobi:{node_core}.appear() done.')
        # finish to call node_core.appear()


    def test_disappear(self):
        node_core = self.node_core

        self.assertFalse(node_core.break_simulation.is_set())

        with self.assertLogs('umatobi', level='INFO') as cm:
            with patch.object(node_core, 'join') as mock_join:
                node_core.disappear()

        self.assertEqual(cm.output[0],
                       f'INFO:umatobi:{node_core}.disappear().')
        self.assertTrue(node_core.break_simulation.is_set())
        mock_join.assert_called_once()
        self.assertEqual(cm.output[1],
                       f'INFO:umatobi:{node_core}.disappear() done.')

if __name__ == '__main__':
    unittest.main()
