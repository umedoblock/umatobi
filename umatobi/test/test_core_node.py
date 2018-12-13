import os
import sys
import threading
import unittest
import queue

from umatobi.p2p.core import Node
from umatobi.lib import current_y15sformat_time
from umatobi.lib import y15sformat_time, y15sformat_parse, make_start_up_orig

class CoreNodeTests(unittest.TestCase):
    def test_p2p_core_node(self):
        node = Node('localhost', 10000)
        self.assertEqual(node.host, 'localhost')
        self.assertEqual(node.port, 10000)

        node.appear()
        node.disappear()

if __name__ == '__main__':
    unittest.main()

