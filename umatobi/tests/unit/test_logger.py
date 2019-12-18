# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

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
from umatobi.log import make_logger

class LoggerTests(unittest.TestCase):

    def setUp(self):
        self.simulation_time = SimulationTime()
        self.path_maker = PathMaker(self.simulation_time)

    def test_make_log_dir(self):
        special_dir = self.path_maker.get_simulation_dir_path()
       #self.assertFalse(os.path.isdir(special_dir))
        tlogger = make_logger(log_dir=special_dir, name='special', id_=None, level="INFO")
        self.assertTrue(os.path.isdir(special_dir))
        shutil.rmtree(special_dir)

        self.assertFalse(os.path.isdir(special_dir))
        tlogger = make_logger(log_dir=special_dir, name='special', id_=10, level="INFO")
        self.assertTrue(os.path.isdir(special_dir))
        shutil.rmtree(special_dir)

        special_dir = self.path_maker.get_simulation_dir_path()
        self.assertFalse(os.path.isdir(special_dir))
        tlogger = make_logger(log_dir=special_dir, name='', id_=None, level="INFO")
        self.assertTrue(os.path.isdir(special_dir))
        shutil.rmtree(special_dir)

        self.assertFalse(os.path.isdir(special_dir))
        tlogger = make_logger(log_dir=special_dir, name='', id_=10, level="INFO")
        self.assertTrue(os.path.isdir(special_dir))
        shutil.rmtree(special_dir)

    def test_log_path(self):
        special_dir = self.path_maker.get_simulation_dir_path()
        tlogger = make_logger(log_dir=special_dir, name='test_logger', id_=None, level="INFO")
        self.assertEqual(tlogger.log_path, os.path.join(special_dir, 'test_logger.log', ))

        special_dir = self.path_maker.get_simulation_dir_path()
        tlogger = make_logger(log_dir=special_dir, name='test_logger', id_=888, level="INFO")
        self.assertEqual(tlogger.log_path, os.path.join(special_dir, 'test_logger.888.log', ))


class LoggerNodeTests(unittest.TestCase):
    def setUp(self):
        self.the_moment = SimulationTime()
        self.path_maker = PathMaker(self.the_moment)
        node_assets = make_node_assets(self.path_maker)

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

        node.master_palm_txt_path = '/tmp/none'
        with self.assertLogs('umatobi', level='DEBUG') as cm:
            ret = node._steal_a_glance_at_master_palm()
        self.assertIsNone(ret)
        mock_path.isfile.assert_called_with(node.master_palm_txt_path)
        self.assertRegex(cm.output[0], f"^INFO:umatobi:not found 'master_palm_txt_path={node.master_palm_txt_path}'")

    def test_steal_master_palm_logger_info2(self):
        node = self.node

        patcher = patch('os.path')
        mock_path = patcher.start()
        mock_path.isfile.return_value = False

        with self.assertLogs('umatobi', level='INFO') as cm:
            ret = node._steal_a_glance_at_master_palm()
        self.assertIsNone(ret)
        mock_path.isfile.assert_called_with(node.master_palm_txt_path)
        self.assertRegex(cm.output[0], f"^INFO:umatobi:not found 'master_palm_txt_path={node.master_palm_txt_path}'")
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
