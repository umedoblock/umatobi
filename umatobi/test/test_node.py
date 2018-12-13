import os
import sys
import threading
import unittest
import queue

from umatobi.simulator.node import Node
from umatobi.lib import current_y15sformat_time
from umatobi.lib import y15sformat_time, y15sformat_parse, make_start_up_orig

class NodeTests(unittest.TestCase):
    def test_node_basic(self):
        good_bye_with_darkness = threading.Event()
        start_up_orig = make_start_up_orig()
        start_up_time = y15sformat_time(start_up_orig)
        _queue_darkness = queue.Queue()
        node_ = Node(host='localhost',
                     port=10001,
                     id=1,
                     good_bye_with_darkness=good_bye_with_darkness,
                     start_up_time=start_up_time,
                     _queue_darkness=_queue_darkness)

        attrs = ('host', 'port', 'id', 'start_up_time', \
                 'good_bye_with_darkness', '_queue_darkness')
        for attr in attrs:
            self.assertTrue(hasattr(node_, attr), attr)

        self.assertFalse(node_._last_moment.is_set())
        node_.appear()
        self.assertFalse(node_._last_moment.is_set())

        node_status = node_.get_status()
        self.assertEqual(dict, type(node_status))

        self.assertFalse(node_.sock._closed)
        self.assertFalse(node_._last_moment.is_set())
        node_.disappear()
        self.assertTrue(node_._last_moment.is_set())
        self.assertTrue(node_.sock._closed)

    def test_node_thread(self):
        good_bye_with_darkness = threading.Event()
        _queue_darkness = queue.Queue()
        start_up_orig = make_start_up_orig()
        start_up_time = y15sformat_time(start_up_orig)

        node_ = Node(host='localhost', port=10001, id=1, good_bye_with_darkness=good_bye_with_darkness, start_up_time=start_up_time, _queue_darkness=_queue_darkness)

        self.assertEqual(1, threading.active_count())
        node_.appear()
        self.assertEqual(2, threading.active_count())

        node_.good_bye_with_darkness.set()
        node_.disappear()
        self.assertEqual(1, threading.active_count())
        self.assertTrue(node_.sock._closed)

if __name__ == '__main__':
    unittest.main()
