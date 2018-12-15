import os
import sys, shutil
import threading, socket
import unittest
import math, queue, pickle

from umatobi.log import logger
from umatobi.simulator.node import Node, NodeOffice
from umatobi.simulator.node import NodeOpenOffice, NodeUDPOffice
from umatobi.lib import current_y15sformat_time
from umatobi.lib import y15sformat_time, y15sformat_parse, make_start_up_orig
from umatobi.lib import dict_becomes_jbytes, jtext_becomes_dict

class NodeTests(unittest.TestCase):
    def setUp(self):
        byebye_nodes = threading.Event()
        start_up_orig = make_start_up_orig()
        start_up_time = y15sformat_time(start_up_orig)
        _queue_darkness = queue.Queue()
        node = Node(host='localhost', port=20001, id=1, byebye_nodes=byebye_nodes, start_up_time=start_up_time, _queue_darkness=_queue_darkness)
        self.node = node
        self._story = True

    def test_steal_master_palm(self):
        self._story = False
        node = self.node
        str_addr = (str(x) for x in node.node_office_addr)
        node_addr_line = f"{':'.join(str_addr)}" + '\n'
        self.assertTrue(hasattr(node, 'master_hand_path'))

        os.makedirs(os.path.dirname(node.master_hand_path), exist_ok=True)
        with open(node.master_hand_path, 'w') as master_palm:
            test_node_lines = "localhost:1223\nlocalhost:2334\n"
            print(test_node_lines, file=master_palm, end='')

        node_lines = node._steal_master_palm()
        self.assertEqual(node_lines, test_node_lines)

        os.remove(node.master_hand_path)

    def test_regist(self):
        self._story = False
        node = self.node
        str_addr = (str(x) for x in node.node_office_addr)
        node_addr_line = f"{':'.join(str_addr)}" + '\n'
        self.assertTrue(hasattr(node, 'master_hand_path'))

        self.assertFalse(os.path.exists(node.master_hand_path))
        node.regist()
        self.assertTrue(os.path.isfile(node.master_hand_path))

        with open(node.master_hand_path) as master_palm:
            master_hand = master_palm.read()
            self.assertEqual(master_hand, node_addr_line)

        node.regist()
        with open(node.master_hand_path) as master_palm:
            master_hand = master_palm.read()
            self.assertEqual(master_hand, node_addr_line * 2)

        os.remove(node.master_hand_path)

    def tearDown(self):
        self.node.sock.close()
        if self._story:
            return
      # self.node.join()

    def test_node_basic(self):
        byebye_nodes = threading.Event()
        start_up_orig = make_start_up_orig()
        start_up_time = y15sformat_time(start_up_orig)
        _queue_darkness = queue.Queue()
        node_ = Node(host='localhost',
                     port=10001,
                     id=1,
                     byebye_nodes=byebye_nodes,
                     start_up_time=start_up_time,
                     _queue_darkness=_queue_darkness)

        attrs = ('host', 'port', 'id', 'start_up_time', \
                 'byebye_nodes', '_queue_darkness')
        for attr in attrs:
            self.assertTrue(hasattr(node_, attr), attr)

        self.assertFalse(node_._last_moment.is_set())
        node_.appear()
        node_.node_office_addr_assigned.wait()
        self.assertEqual((node_.host, node_.port), node_.node_office_addr)
        self.assertFalse(node_._last_moment.is_set())

        tup = node_._queue_darkness.get()
        et, pickle_dumps = tup
        d = pickle.loads(pickle_dumps)
        self.assertEqual(d['id'], 1)
        self.assertEqual(d['id'], node_.id)
        self.assertEqual(d['host'], 'localhost')
        self.assertEqual(d['host'], node_.host)
        self.assertEqual(d['port'], node_.port)
        self.assertRegex(d['key'], r'\A0x\w{32}\Z')
        self.assertNotIn(d['key'], '_')
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

        node_status = node_.get_status()
        self.assertEqual(dict, type(node_status))

        node_.byebye_nodes.set() # act darkness

        self.assertFalse(node_.sock._closed)
        self.assertFalse(node_._last_moment.is_set())
        node_.disappear()
        self.assertTrue(node_._last_moment.is_set())
        self.assertTrue(node_.sock._closed)

        os.remove(node_.master_hand_path)

    def test_node_thread(self):
        logger.info(f"")
        byebye_nodes = threading.Event()
        _queue_darkness = queue.Queue()
        start_up_orig = make_start_up_orig()
        start_up_time = y15sformat_time(start_up_orig)

        node_ = Node(host='localhost', port=10001, id=1, byebye_nodes=byebye_nodes, start_up_time=start_up_time, _queue_darkness=_queue_darkness)

        logger.info(f"node_.appear()")
        node_.appear()
        node_.node_office_addr_assigned.wait()
        self.assertEqual((node_.host, node_.port), node_.node_office_addr)
        self.assertEqual(3, threading.active_count())

        logger.info(f"node_.byebye_nodes.set()")
        node_.byebye_nodes.set() # act darkness
        logger.info(f"node_.disappear()")
        node_.disappear()
        for th in threading.enumerate():
            print(f"th={th}")
        self.assertEqual(1, threading.active_count())
        self.assertTrue(node_.sock._closed)

        os.remove(node_.master_hand_path)

class NodeOfficeTests(unittest.TestCase):

    def setUp(self):
        byebye_nodes = threading.Event()
        start_up_orig = make_start_up_orig()
        start_up_time = y15sformat_time(start_up_orig)
        _queue_darkness = queue.Queue()
        node = Node(host='localhost', port=20001, id=1, \
                    byebye_nodes=byebye_nodes, \
                    start_up_time=start_up_time, \
                    _queue_darkness=_queue_darkness)
        self.node = node

    def test_handle(self):
        node = self.node
        node._open_office()
        node._init_node()

        client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_address = ('localhost', 8888)
        client_sock.bind(client_address)
        server = NodeUDPOffice(node)

        d = {
            'profess': 'You are Red.',
            'hop': 1,
        }
        packet = dict_becomes_jbytes(d)
        request = packet, client_sock
        print('request =', request)
        node_office = \
            NodeOffice(request, client_address, server)
        server.server_close()

        node.node_udp_office.shutdown()

        recved = client_sock.recvfrom(1024)
        packet, client_socket = recved

        print("       recved =", recved)
        print("       packet =", packet)
        print("client_socket =", client_socket)
        d_recved = jtext_becomes_dict(packet)
        self.assertEqual(d_recved['hop'], d['hop'] * 2)
        self.assertEqual(d_recved['profess'], 'You are Green.')

        client_sock.close()
        node.sock.close()

if __name__ == '__main__':
    unittest.main()
