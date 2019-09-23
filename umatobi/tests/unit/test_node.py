import os
import sys, shutil
import threading, socket
import unittest, time
import math, pickle
from unittest.mock import patch

import umatobi
from umatobi.lib import *
from umatobi.tests import *
from umatobi.log import logger
from umatobi.simulator.core.key import Key
from umatobi.simulator.node import *

# class NodeOpenOfficeTests(unittest.TestCase):

class NodeUDPOfficeTests(unittest.TestCase):
    def test__determine_node_office_addr_every_ports_are_in_use(self):
        node_assets = make_node_assets()
        node = Node(id=48, host='localhost', **node_assets)

        with self.assertRaises(RuntimeError) as cm:
            with patch('socket.socket.bind',
                    side_effect=OSError(4848484848,
                                    'Address already in use')) as mock_bind:
                server = NodeUDPOffice(node)
        the_exception = cm.exception
        self.assertEqual(the_exception.args[0], 'every ports are in use.')

    def test__determine_node_office_addr(self):
        node_assets = make_node_assets()
        node = Node(id=48, host='localhost', **node_assets)

        side_effects = [OSError(22222222, 'Address already in use'), None]
        with patch('socket.socket.bind', side_effect=side_effects) as mock_bind:
            server = NodeUDPOffice(node)

        server.server_close()

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

class NodeTests(unittest.TestCase):
    def assertIsPort(self, port):
        self.assertGreaterEqual(port, 1024)
        self.assertLessEqual(port, 65535)

    def setUp(self):
        self.simulation_time = SimulationTime()
        self.simulation_dir_path = \
                get_simulation_dir_path(self.simulation_time)

        os.makedirs(self.simulation_dir_path, exist_ok=True)

        self.the_moment = SimulationTime.now()
        with time_machine(self.the_moment):
            node_assets = make_node_assets()
        node = Node(host='localhost', id=1, **node_assets)
        key = b'\x01\x23\x45\x67\x89\xab\xcd\xef' * 4
        node.key.update(key)
        self.node = node
        self.key = key

    def tearDown(self):
        self.node.release()

#   def test_run(self):
#   def test__open_office(self):
#   def test__force_shutdown(self):
#   def test_set_attrs(self):
#   def test_get_elapsed_time(self):
#   def test_appear(self):
#   def test_disappear(self):
#   def test_release_clients(self):
#   def test___str__(self):

    def test_node_thread(self):
        logger.info(f"")
        node_assets = make_node_assets()
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

        os.remove(node_.master_palm_path)

    def test_node_basic(self):
        node_assets = make_node_assets()
        node_ = Node(host='localhost', id=1, **node_assets)
        self.assertFalse(node_.im_ready.is_set())

        attrs = ('id', 'iso8601', \
                 'byebye_nodes', '_queue_darkness')
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

        os.remove(node_.master_palm_path)

    def test_node_get_info(self):
        node_assets = make_node_assets()
        node = Node(host='localhost', port=55555, **node_assets)
        node_info_line = f"{node.office_addr[0]}:{node.office_addr[1]}:{str(node.key)}" + '\n'
        self.assertEqual(node.office_addr[0], 'localhost')
        self.assertEqual(node.office_addr[1], 55555)
        self.assertEqual(node.get_info(), node_info_line)

        node.release()

    def test_regist(self):
        node = self.node

        node.port = 63333
        self.assertTrue(hasattr(node, 'master_palm_path'))

        self.assertFalse(os.path.exists(node.master_palm_path))
        self.assertFalse(node.im_ready.is_set())
        node.regist() # once
        self.assertTrue(node.im_ready.is_set())
        self.assertTrue(os.path.isdir(os.path.dirname(node.master_palm_path)))
        self.assertTrue(os.path.isfile(node.master_palm_path))

        with open(node.master_palm_path) as master_palm:
            master_palm_on = master_palm.read()
            self.assertEqual(master_palm_on, node.get_info())

        node.regist() # twice
        with open(node.master_palm_path) as master_palm:
            master_palm_on2 = master_palm.read()
            self.assertEqual(master_palm_on2, node.get_info() * 2)

        os.remove(node.master_palm_path)

    def test__steal_a_glance_at_master_palm(self):
        iso8601 = SimulationTime().get_iso8601()
        node = self.node
        node2 = Node(host='localhost', port=11112, iso8601=iso8601)
        node3 = Node(host='localhost', port=11113, iso8601=iso8601)
        self.assertTrue(hasattr(node, 'master_palm_path'))

        master_palm_on = node2.get_info() + node3.get_info()

        with open(node.master_palm_path, 'w') as master_palm:
            print(node2.get_info(), file=master_palm, end='')
            print(node3.get_info(), file=master_palm, end='')

        node_lines = node._steal_a_glance_at_master_palm()
        self.assertEqual(node_lines, master_palm_on)
        os.remove(node.master_palm_path)

        node2.release()
        node3.release()

    @patch('os.path')
    def test_steal_a_glance_at_master_palm_logger_info(self, mock_path):
        mock_path.isfile.return_value = False

        node = self.node

        self.master_palm_path = '/tmp/none'
        with self.assertLogs('umatobi', level='INFO') as cm:
            ret = node._steal_a_glance_at_master_palm()
        self.assertIsNone(ret)
        mock_path.isfile.assert_called_with(node.master_palm_path)
        self.assertRegex(cm.output[0], f"^INFO:umatobi:not found 'master_palm_path={node.master_palm_path}'")

    def test_steal_a_glance_at_master_palm_logger_info2(self):
        node = self.node

        patcher = patch('os.path')
        mock_path = patcher.start()
        mock_path.isfile.return_value = False

        with self.assertLogs('umatobi', level='INFO') as cm:
            ret = node._steal_a_glance_at_master_palm()
        self.assertIsNone(ret)
        mock_path.isfile.assert_called_with(node.master_palm_path)
        self.assertRegex(cm.output[0], f"^INFO:umatobi:not found 'master_palm_path={node.master_palm_path}'")
        patcher.stop()

    def test_get_attrs(self):
        node = self.node

        attrs = node.get_attrs()
        self.assertSetEqual(set(attrs.keys()), set(Node.ATTRS))

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

    def test_update_key(self):
        node = self.node

        self.assertEqual(node.key.key, self.key)
        key = b'\xfe\xdc\xba\x98\x76\x54\x32\x10' * 4
        node.key.update(key)
        self.assertEqual(node.key.key, key)

if __name__ == '__main__':
    unittest.main()
