import os
import sys
import threading
import unittest
import queue

import umatobi.p2p.core
import umatobi.simulator.node

class TestNode(unittest.TestCase):
    def test_p2p_core_node(self):
        p2p_core_Node = umatobi.p2p.core.Node('localhost', 10000)
        node_status = p2p_core_Node.get_status()
        self.assertEqual(dict, type(node_status))

        self.assertEqual(1, threading.active_count())
        p2p_core_Node.appear()
        self.assertEqual(2, threading.active_count())

        p2p_core_Node.disappear()
        self.assertEqual(1, threading.active_count())

    def test_simulator_node(self):
        good_bye_with_nodes = threading.Event()
        _queue_darkness = queue.Queue()
        node_ = \
            umatobi.simulator.node.Node('localhost', 10001, 0, good_bye_with_nodes,
                                 _queue_darkness)

        node_status = node_.get_status()
        self.assertEqual(dict, type(node_status))

        self.assertEqual(1, threading.active_count())
        node_.appear()
        self.assertEqual(2, threading.active_count())

        good_bye_with_nodes.set()
      # print(node_status)
        node_.disappear()
        self.assertEqual(1, threading.active_count())

if __name__ == '__main__':
    unittest.main()
