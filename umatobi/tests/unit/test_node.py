import os
import sys, shutil
import threading, socket
import unittest
import math, queue, pickle

from umatobi.tests import *
from umatobi.log import logger
from umatobi.simulator.node import Node, NodeOffice
from umatobi.simulator.node import NodeOpenOffice, NodeUDPOffice
from umatobi.lib import current_y15sformat_time
from umatobi.lib import y15sformat_time, y15sformat_parse, make_start_up_orig
from umatobi.lib import dict2json, json2dict
from umatobi.tests.lib import escape_ResourceWarning

class NodeTests(unittest.TestCase):
    def setUp(self):
        byebye_nodes = threading.Event()
        start_up_orig = make_start_up_orig()
        start_up_time = y15sformat_time(start_up_orig)
        _queue_darkness = queue.Queue()
        node = Node(host='localhost', id=1, byebye_nodes=byebye_nodes, start_up_time=start_up_time, _queue_darkness=_queue_darkness)
        key = b'\x01\x23\x45\x67\x89\xab\xcd\xef' * 4
        node.update_key(key)
        self.node = node
        self.key = key

    def tearDown(self):
        self.node.release()

    def test_to_darkness(self):
#       db['nodes']
#       db['clients']
#       db['nodes']
       #node = self.node
       #node.to_darkness(d)

       #et = elapsed_time(y15sformat_parse(node.start_up_time))
       #d_attrs = self.get_attrs()
       #self.to_darkness(d_attrs, et)

    def test_update_key(self):
        node = self.node

        self.assertEqual(node.key, self.key)
        key = b'\xfe\xdc\xba\x98\x76\x54\x32\x10' * 4
        node.update_key(key)
        self.assertEqual(node.key, key)

    def test_node_get_info(self):
        node = self.node
        node_info_line = f"{node.office_addr[0]}:{node.office_addr[1]}:{str(node.key_hex)}" + '\n'
        self.assertEqual(node.get_info(), node_info_line)

    def test_steal_master_palm(self):
        node = self.node
        node2 = Node(host='localhost', port=11112, start_up_time=node.start_up_time)
        node3 = Node(host='localhost', port=11113, start_up_time=node.start_up_time)
        self.assertTrue(hasattr(node, 'master_hand_path'))

        master_palm_on = node2.get_info() + node3.get_info()

        os.makedirs(os.path.dirname(node.master_hand_path), exist_ok=True)
        with open(node.master_hand_path, 'w') as master_palm:
            print(node2.get_info(), file=master_palm, end='')
            print(node3.get_info(), file=master_palm, end='')

        node_lines = node._steal_master_palm()
        self.assertEqual(node_lines, master_palm_on)
        os.remove(node.master_hand_path)

        escape_ResourceWarning(node2.udp_sock)
        escape_ResourceWarning(node3.udp_sock)

    def test_regist(self):
        node = self.node

        node.port = 63333
        self.assertTrue(hasattr(node, 'master_hand_path'))

        self.assertFalse(os.path.exists(node.master_hand_path))
        node.regist() # once
        self.assertTrue(os.path.isdir(os.path.dirname(node.master_hand_path)))
        self.assertTrue(os.path.isfile(node.master_hand_path))

        with open(node.master_hand_path) as master_palm:
            master_hand_on = master_palm.read()
            self.assertEqual(master_hand_on, node.get_info())

        node.regist() # twice
        with open(node.master_hand_path) as master_palm:
            master_hand_on2 = master_palm.read()
            self.assertEqual(master_hand_on2, node.get_info() * 2)

        os.remove(node.master_hand_path)

    def test_node_basic(self):
        byebye_nodes = threading.Event()
        start_up_orig = make_start_up_orig()
        start_up_time = y15sformat_time(start_up_orig)
        _queue_darkness = queue.Queue()
        node_ = Node(host='localhost', id=1,
                     byebye_nodes=byebye_nodes,
                     start_up_time=start_up_time,
                     _queue_darkness=_queue_darkness)

        attrs = ('id', 'start_up_time', \
                 'byebye_nodes', '_queue_darkness')
        for attr in attrs:
            self.assertTrue(hasattr(node_, attr), attr)

        node_.appear()

        node_.office_addr_assigned.wait()
        self.assertIsInstance(node_.office_addr, tuple)
        self.assertEqual(node_.office_addr[0], 'localhost')
        self.assertIsInstance(node_.office_addr[1], int)
        self.assertGreaterEqual(node_.office_addr[1], 1024)
        self.assertLessEqual(node_.office_addr[1], 65535)

        tup = node_._queue_darkness.get()
        et, pickle_dumps = tup
        d = pickle.loads(pickle_dumps)
        self.assertEqual(d['id'], 1)
        self.assertEqual(d['id'], node_.id)

        self.assertEqual(d['office_addr'][0], 'localhost')
        self.assertIsInstance(d['office_addr'][1], int)
        self.assertGreaterEqual(d['office_addr'][1], 1024)
        self.assertLessEqual(d['office_addr'][1], 65535)

        self.assertRegex(d['key_hex'], r'\A0x\w{64}\Z')
        self.assertNotIn(d['key_hex'], '_')
        self.assertIsInstance(d['rad'], float)
        self.assertGreaterEqual(d['rad'], 0.0)
        self.assertLessEqual(d['rad'], 2 * math.pi)
        self.assertIsInstance(d['x'], float)
        self.assertGreaterEqual(d['x'], -1.0)
        self.assertLessEqual(d['x'], 1.0)
        self.assertIsInstance(d['y'], float)
        self.assertGreaterEqual(d['y'], -1.0)
        self.assertLessEqual(d['y'], 1.0)
        self.assertEqual(d['status'], 'active')

        node_.byebye_nodes.set() # act darkness

        node_.disappear()

        os.remove(node_.master_hand_path)

    def test_node_thread(self):
        logger.info(f"")
        byebye_nodes = threading.Event()
        _queue_darkness = queue.Queue()
        start_up_orig = make_start_up_orig()
        start_up_time = y15sformat_time(start_up_orig)

        node_ = Node(host='localhost', id=1, byebye_nodes=byebye_nodes, start_up_time=start_up_time, _queue_darkness=_queue_darkness)

        logger.info(f"node_.appear()")
        node_.appear()
        node_.office_addr_assigned.wait()
        self.assertEqual(node_.office_addr, node_.office_addr)
        self.assertEqual(3, threading.active_count())

        logger.info(f"node_.byebye_nodes.set()")
        node_.byebye_nodes.set() # act darkness
        logger.info(f"node_.disappear()")
        node_.disappear()
        for th in threading.enumerate():
            print(f"th={th}")
        self.assertEqual(1, threading.active_count())

        os.remove(node_.master_hand_path)

class NodeOfficeTests(unittest.TestCase):
    def setUp(self):
        byebye_nodes = threading.Event()
        start_up_orig = make_start_up_orig()
        start_up_time = y15sformat_time(start_up_orig)
        _queue_darkness = queue.Queue()
        node = Node(id=1, host='localhost', \
                    byebye_nodes=byebye_nodes, \
                    start_up_time=start_up_time, \
                    _queue_darkness=_queue_darkness)
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

if __name__ == '__main__':
    unittest.main()
