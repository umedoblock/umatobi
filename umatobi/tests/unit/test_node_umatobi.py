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
import math, pickle
from unittest.mock import patch, MagicMock, mock_open, call

import umatobi
from umatobi.lib import *
from umatobi.tests import *
from umatobi.log import logger
from umatobi.simulator.key import Key
from umatobi.simulator.node import *

class NodeOpenOfficeTests(unittest.TestCase):

    def test___init__(self):
        pass

    def test_run(self):
        pass

class NodeUDPOfficeTests(unittest.TestCase):

    def test___init__(self):
        pass

    def test_server_bind(self):
        pass

    def test__determine_node_office_addr(self):
        node_assets = make_node_assets()
        node = Node(id=48, host='localhost', **node_assets)

        server = NodeUDPOffice(node)
        self.assertEqual(server.node, node)
        self.assertIsInstance(server.socket, socket.socket)
        self.assertEqual(server.clients, [])
        self.assertEqual(server.RequestHandlerClass, NodeOffice)
        self.assertEqual(server.node.office_addr[0], 'localhost')
        self.assertEqual(server.server_address[0], '127.0.0.1')
        # same port
        self.assertEqual(server.node.office_addr[1], server.server_address[1])

        server.server_close()

    def test__determine_node_office_addr_fail_by_OSError(self):
        node_assets = make_node_assets()
        node = Node(id=48, host='localhost', **node_assets)

        side_effects = [OSError(22222222, 'Address already in use'), None]
        with patch('socket.socket.bind', side_effect=side_effects) as mock_bind:
            server = NodeUDPOffice(node)

        server.server_close()

    def test_serve_forever(self):
        pass

    def test__determine_node_office_addr_all_ports_are_in_use(self):
        node_assets = make_node_assets()
        node = Node(id=48, host='localhost', **node_assets)

        with self.assertRaises(RuntimeError) as cm:
            with patch('socket.socket.bind',
                    side_effect=OSError(4848484848,
                                    'Address already in use')) as mock_bind:
                server = NodeUDPOffice(node)
        the_exception = cm.exception
        self.assertEqual(the_exception.args[0], 'all ports are in use.')

class NodeOfficeTests(unittest.TestCase):
    def setUp(self):
        node_assets = make_node_assets()
        node = Node(id=1, host='localhost', **node_assets)
        self.node = node

    def test_handle(self):
        node = self.node
        node._open_office()

        client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_address = ('localhost', 8888)
        client_sock.bind(client_address)
        server = NodeUDPOffice(node)

        d = {
            'profess': 'You are Red.',
            'hop': 1,
        }
        packet = dict2json(d)
        request = packet.encode('utf-8'), client_sock
      # print('request =', request)
        node_office = NodeOffice(request, client_address, server)
        node.node_udp_office.shutdown()

        recved = client_sock.recvfrom(1024)
        packet, client_socket = recved
        client_sock.close()
      # server.server_close() # あってもなくても正常終了する
        # 正常終了自体は、本当ですが、
        # ResourceWarning: unclosed <socket.socket fd=8, ...
        # ResourceWarning: Enable tracemalloc to get the object allocation traceback
        # と、うるさいので、server.server_close()を忘れずに実行しましょう。
        server.server_close()
        # ずっと苦労していた bug 取りでしたが、過去にきちんと書いてたんだ。。。
        # 勝手に消してしまったばかりに。。。苦労したよ。。。

      # print("       recved =", recved)
      # print("       packet =", packet)
      # print("client_socket =", client_socket)
        d_recved = json2dict(packet.decode())
        self.assertEqual(d_recved['hop'], d['hop'] * 2)
        self.assertEqual(d_recved['profess'], 'You are Green.')

    def test_finish(self):
        pass

class NodeTests(unittest.TestCase):
    def assertIsPort(self, port):
        self.assertGreaterEqual(port, 1024)
        self.assertLessEqual(port, 65535)

    @classmethod
    def setUpClass(cls):
        cls.path_maker = PathMaker()

    @classmethod
    def tearDownClass(cls):
        cls.path_maker = None

    def setUp(self):
        node_assets = make_node_assets(NodeTests.path_maker)

        node = Node(host='localhost', id=1, **node_assets)
        key = b'\x01\x23\x45\x67\x89\xab\xcd\xef' * 4
        node.key.update(key)
        self.node = node
        self.key = key

    def tearDown(self):
        self.node.release()

    @patch('umatobi.simulator.node.threading.Lock')
    def test___init__(self, mock_lock):
        node_assets = make_node_assets(NodeTests.path_maker)
        node = Node(addr='localhost', id=0, **node_assets)

        self.assertIsInstance(node.key, Key)
        self.assertEqual(node.status, 'active')

        self.assertEqual(node.nodes, [])
        self.assertFalse(node.im_ready.is_set())
        self.assertIsInstance(node.office_door, MagicMock)
        mock_lock.assert_called_with()
        self.assertFalse(node.office_addr_assigned.is_set())

        self.assertEqual(node.master_palm_txt_path,
                         node.path_maker.get_master_palm_txt_path())

    def test_run(self):
        pass

    def test__open_office(self):
        pass

    def test_get_info(self):
        pass

    def test_regist(self):
        node = self.node

        node.office_addr = ('localhost', 63333)

        self.assertFalse(node.im_ready.is_set())

        m_o = mock_open()
        with patch('umatobi.simulator.node.open', m_o):
            node.regist() # once

           #print(m_o.mock_calls)
           #print(node.get_info())
            m_o.assert_called_once_with(node.master_palm_txt_path, 'a')
            self.assertEqual(m_o().write.call_args_list,
                    [call(f'localhost:63333:{node.key}\n'),
                     call("")])

            self.assertTrue(node.im_ready.is_set())
            self.assertTrue(os.path.isdir(os.path.dirname(node.master_palm_txt_path)))

            with patch('umatobi.simulator.node.open', m_o):
                node.regist() # twice
           #print(m_o.mock_calls)
           #print(m_o().write.call_args_list)
            self.assertEqual(m_o().write.call_args_list,
                    [call(f'localhost:63333:{node.key}\n'),
                     call(""),
                     call(f'localhost:63333:{node.key}\n'),
                     call("")])

    @patch('os.path.isfile', return_value=True)
    def test__steal_a_glance_at_master_palm(self, mock_isfile):
        node = self.node
        node2 = Node(host='localhost', port=11112, path_maker=self.path_maker)
        node3 = Node(host='localhost', port=11113, path_maker=self.path_maker)
        self.assertTrue(hasattr(node, 'master_palm_txt_path'))

        master_palm_on = node2.get_info() + node3.get_info()

        with self.assertLogs('umatobi', level='INFO') as cm:
            with patch('umatobi.simulator.node.open',
                        mock_open(read_data=master_palm_on)) as m:
                node_lines = node._steal_a_glance_at_master_palm()

        self.assertEqual(cm.output[0], f"INFO:umatobi:found 'master_palm_txt_path={node.master_palm_txt_path}'")
        self.assertEqual(node_lines, master_palm_on)
        mock_isfile.assert_called_once_with(node.master_palm_txt_path)

        node2.release()
        node3.release()

    def test__force_shutdown(self):
        pass

    def test_set_attrs(self):
        pass

    def test_get_attrs(self):
        node = self.node
        expected_attrs = {
            'id': 1,
            'office_addr': ('localhost', None),
            'key': Key(b'\x01\x23\x45\x67\x89\xab\xcd\xef' * 4),
            'status': 'active',
            'path_maker': NodeTests.path_maker,
        }

        attrs = node.get_attrs()
        self.assertEqual(attrs, expected_attrs)

    def test_put_on_darkness(self):
        node = self.node

        et = node.get_elapsed_time()
        attrs = node.get_attrs()

        self.assertEqual(node._queue_darkness.qsize(), 0)
        node.put_on_darkness(attrs, et)
        self.assertEqual(node._queue_darkness.qsize(), 1)

        got_et, got_pickled = node._queue_darkness.get()
        self.assertEqual(node._queue_darkness.qsize(), 0)
        got_d_attrs = pickle.loads(got_pickled)
        self.assertEqual(got_et, et)
        self.assertEqual(got_d_attrs, attrs)

    def test_get_elapsed_time(self):
        pass

    def test_appear(self):
        pass

    def test_disappear(self):
        pass

    def test_release_clients(self):
        pass

    def test___str__(self):
        pass

    def test_update(self):
        pass

    def test_node_thread(self):
        logger.info(f"")
        node_assets = make_node_assets(path_maker=NodeTests.path_maker)
        node_ = Node(host='localhost', id=1, **node_assets)

        logger.info(f"node_.appear()")
        node_.appear()
        node_.office_addr_assigned.wait()
        self.assertEqual(node_.office_addr, node_.office_addr)
        self.assertEqual(3, threading.active_count())

        logger.info(f"node_.byebye_nodes.set()")
        node_.byebye_nodes.set() # act darkness
        logger.info(f"node_.disappear()")
        node_.disappear()
        self.assertEqual(1, threading.active_count())

        os.remove(node_.master_palm_txt_path)

    def test_node_basic(self):
        node_assets = make_node_assets(path_maker=NodeTests.path_maker)
        node_ = Node(host='localhost', id=1, **node_assets)
        self.assertFalse(node_.im_ready.is_set())

        attrs = ('id', 'path_maker', 'byebye_nodes', '_queue_darkness')
        for attr in attrs:
            self.assertTrue(hasattr(node_, attr), attr)

      # node.start()
        node_.appear()
        node_.regist() # node_.im_ready.set()
        self.assertTrue(node_.im_ready.is_set())

        node_.office_addr_assigned.wait()
        self.assertIsInstance(node_.office_addr, tuple)
        self.assertEqual(node_.office_addr[0], 'localhost')
        self.assertIsPort(node_.office_addr[1])

        tup = node_._queue_darkness.get()
        et, pickle_dumps = tup
        d = pickle.loads(pickle_dumps)
        self.assertEqual(d['id'], 1)
        self.assertEqual(d['id'], node_.id)

        self.assertEqual(d['office_addr'][0], 'localhost')
        self.assertIsPort(d['office_addr'][1])

        self.assertIsInstance(d['key'], Key)
        self.assertEqual(d['status'], 'active')

        node_.byebye_nodes.set() # act darkness

        node_.disappear()

        os.remove(node_.master_palm_txt_path)

    def test_node_get_info(self):
        node_assets = make_node_assets()
        node = Node(host='localhost', port=55555, **node_assets)
        node_info_line = f"{node.office_addr[0]}:{node.office_addr[1]}:{str(node.key)}" + '\n'
        self.assertEqual(node.office_addr[0], 'localhost')
        self.assertEqual(node.office_addr[1], 55555)
        self.assertEqual(node.get_info(), node_info_line)

        node.release()

    @patch('os.path')
    def test_steal_a_glance_at_master_palm_logger_info(self, mock_path):
        mock_path.isfile.return_value = False

        node = self.node

        self.master_palm_txt_path = '/tmp/none'
        with self.assertLogs('umatobi', level='INFO') as cm:
            ret = node._steal_a_glance_at_master_palm()
        self.assertIsNone(ret)
        mock_path.isfile.assert_called_with(node.master_palm_txt_path)
        self.assertRegex(cm.output[0], f"^INFO:umatobi:not found 'master_palm_txt_path={node.master_palm_txt_path}'")

    def test_steal_a_glance_at_master_palm_logger_info2(self):
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

    def test_update_key(self):
        node = self.node

        self.assertEqual(node.key.key, self.key)
        key = b'\xfe\xdc\xba\x98\x76\x54\x32\x10' * 4
        node.key.update(key)
        self.assertEqual(node.key.key, key)

if __name__ == '__main__':
    unittest.main()
