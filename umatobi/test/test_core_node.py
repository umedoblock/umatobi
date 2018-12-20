import os
import sys
import threading
import unittest
import queue

from umatobi.p2p.core import Node
from umatobi.lib import current_y15sformat_time
from umatobi.lib import y15sformat_time, y15sformat_parse, make_start_up_orig

class CoreNodeTests(unittest.TestCase):
    def test_core_node_init(self):
        node = Node('localhost', 10000)
        self.assertEqual(node.host, 'localhost')
        self.assertEqual(node.port, 10000)
        self.assertTrue(hasattr(node, 'key'))

        node.appear()
        self.assertFalse(node._last_moment.is_set())

        node.disappear()
        self.assertTrue(node._last_moment.is_set())
        self.assertTrue(node.sock._closed)

    def test_core_node_key(self):
        node = Node('localhost', 10000)
        self.assertTrue(hasattr(node, 'key'))
        self.assertIsInstance(node.key, bytes)

        key0 = node.key
        node.update_key()
        self.assertNotEqual(node.key, key0)

        key_rand = os.urandom(32)
        node.update_key(key_rand)
        self.assertEqual(node.key, key_rand)

        node.sock.close()

    def test_core_keyhex(self):
        node = Node('localhost', 10000)

        node.update_key()
        self.assertEqual(int(node._key_hex(), 16),
                         int.from_bytes(node.key, 'big'))

        node.sock.close()

    def test_core_node_thread(self):
        node = Node('localhost', 10000)

        node_status = node.get_status()
        self.assertEqual(dict, type(node_status))
        self.assertEqual(1, threading.active_count())

        node.appear()
        self.assertEqual(2, threading.active_count())

        node.disappear()
        self.assertEqual(1, threading.active_count())

if __name__ == '__main__':
    unittest.main()

