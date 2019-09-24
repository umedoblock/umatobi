import os
import sys, shutil
import threading, socket
import unittest, time
import math, queue, pickle
from unittest.mock import patch
from unittest import mock

import umatobi
from umatobi.lib import *
from umatobi.tests import *
from umatobi.simulator.client import Client
from umatobi.simulator.node import Node
from umatobi import lib

class LoggerNodeTests(unittest.TestCase):
    def setUp(self):
        self.the_moment = lib.make_start_up_orig()
        with time_machine(self.the_moment):
            node_assets = Node.make_node_assets()
        node = Node(host='localhost', id=1, **node_assets)
        key = b'\x01\x23\x45\x67\x89\xab\xcd\xef' * 4
        node.key.update(key)
        self.node = node
        self.key = key

    def tearDown(self):
        self.node.release()

    @patch('os.path')
    def test_steal_master_palm_logger_info(self, mock_path):
        mock_path.isfile.return_value = False

        node = self.node

        self.master_hand_path = '/tmp/none'
        with self.assertLogs('umatobi', level='DEBUG') as cm:
            ret = node._steal_master_palm()
        self.assertIsNone(ret)
        mock_path.isfile.assert_called_with(node.master_hand_path)
        self.assertRegex(cm.output[0], f"^INFO:umatobi:not found 'master_hand_path={node.master_hand_path}'")

    def test_steal_master_palm_logger_info2(self):
        node = self.node

        patcher = patch('os.path')
        mock_path = patcher.start()
        mock_path.isfile.return_value = False

        with self.assertLogs('umatobi', level='INFO') as cm:
            ret = node._steal_master_palm()
        self.assertIsNone(ret)
        mock_path.isfile.assert_called_with(node.master_hand_path)
        self.assertRegex(cm.output[0], f"^INFO:umatobi:not found 'master_hand_path={node.master_hand_path}'")
        patcher.stop()

class LoggerClientTests(unittest.TestCase):
    def test_client__waits_to_break_down(self):
        watson_office_addr = ('localhost', 11111)
        num_nodes = 10

        client = Client(watson_office_addr, num_nodes)

        client._tcp_sock = mock.MagicMock()
        client._tcp_sock.recv.return_value = b'break down.'
        with self.assertLogs('umatobi', level='INFO') as cm:
            recved_mail = client._waits_to_break_down()
        self.assertEqual(recved_mail, b'break down.')
        self.assertRegex(cm.output[0], r'^INFO:umatobi:.*\._waits_to_break_down\(\)')

if __name__ == '__main__':
    unittest.main()
