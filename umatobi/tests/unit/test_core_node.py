import os, sys, threading, socket, queue
import unittest

from umatobi.simulator.core.node import Node

class CoreNodeTests(unittest.TestCase):

    def test___init__(self):
        pass

    def test_release(self):
        pass

    def test_not_ready(self):
        node = Node()
        self.assertIsNone(node.udp_sock)

    def test_not_ready1(self):
        node = Node(host='127.0.0.1')
        self.assertIsNone(node.udp_sock)

    def test_not_ready2(self):
        node = Node(host='localhost')
        self.assertIsNone(node.udp_sock)

    def test_not_ready3(self):
        node = Node(port=None)
        self.assertIsNone(node.udp_sock)

    def test_make_udpip_success(self):
        node = Node()
        self.assertIsNone(node.udp_sock)
        self.assertEqual(node.udp_ip, (None, None))
        ret = node.make_udpip('localhost', 4444)
        self.assertTrue(ret)
        self.assertIsInstance(node.udp_sock, socket.socket)
        self.assertEqual(node.udp_ip, ('localhost', 4444))

        node.release()

    def test_make_udpip_doesnt_make_udpip(self):
        pairs_of_host_port = [(None, 4444), ('localhost', None), (None, None)]

        for host, port in pairs_of_host_port:
            node = Node()
            self.assertIsNone(node.udp_sock)
            self.assertEqual(node.udp_ip, (None, None))
            ret = node.make_udpip(host, port)
            self.assertFalse(ret)
            self.assertIsNone(node.udp_sock)
            self.assertEqual(node.udp_ip, (host, port))

    def test_make_udpip_got_on_the_boundary_port(self):
        for on_the_boundary_port in (1024, 65535):
            node = Node()
            self.assertIsNone(node.udp_sock)
            self.assertEqual(node.udp_ip, (None, None))
            ret = node.make_udpip('localhost', on_the_boundary_port)
            self.assertTrue(ret)
            self.assertIsInstance(node.udp_sock, socket.socket)
            self.assertEqual(node.udp_ip, ('localhost', on_the_boundary_port))

            node.release()

    def test_make_udpip_got_a_sensitive_port(self):
        # Can you bind system ports ?
        for sensitive_port in (0, 1, 1023):
            node = Node()
            self.assertIsNone(node.udp_sock)
            self.assertEqual(node.udp_ip, (None, None))
            with self.subTest(sensitive_port=sensitive_port):
                ret = node.make_udpip('localhost', sensitive_port)
                if ret:
                    # Really !!! You can bind a sensitive port.
                    # Are you root ?
                    # You must study security.
                    # You must open many security holes.
                    self.assertIsInstance(node.udp_sock, socket.socket)
                    self.assertEqual(node.udp_ip, ('localhost', sensitive_port))

                    node.release()
                else:
                    # You cannot bind a sensitive port.
                    # You have a good security policy.
                    self.assertIsNone(node.udp_sock)
                    # However port must be set. for debug.
                    self.assertEqual(node.udp_ip, ('localhost', sensitive_port))

    def test_make_udpip_got_out_of_range_port(self):
      # OverflowError: getsockaddrarg: port must be 0-65535.
        for invalid_port in (-1, 65535 + 1):
            node = Node()
            self.assertIsNone(node.udp_sock)
            self.assertEqual(node.udp_ip, (None, None))
            ret = node.make_udpip('localhost', invalid_port)
            self.assertFalse(ret)
            self.assertIsNone(node.udp_sock)
            self.assertEqual(node.udp_ip, ('localhost', invalid_port))
            # except OverflowError で、範囲外と理解しているので、
            # invalid_port が設定されていても OK.

    def test_run(self):
        pass

    def test_appear(self):
        pass

    def test_disappear(self):
        pass

    def test_get_status(self):
        pass

    def test_core_node_init_success(self):
        node = Node('localhost', 20000)
        self.assertEqual(node.udp_ip, ('localhost', 20000))
        self.assertIsInstance(node._last_moment, threading.Event)
        self.assertIsInstance(node._status, dict)
        self.assertIsInstance(node.udp_sock, socket.socket)

        node.release()

    def test_core_node_not_ready(self):
        node = Node()
        self.assertTrue(node.not_ready())

    def test_core_node_init_fail(self):
        pairs_of_host_port = [('', 10000), ('localhost', None)]
        for host, port in pairs_of_host_port:
            node = Node(host, port)
            self.assertTrue(node.not_ready())
            self.assertEqual(node.udp_ip, (host, port))
            self.assertIsInstance(node._last_moment, threading.Event)
            self.assertIsInstance(node._status, dict)
            self.assertIsNone(node.udp_sock)

    def test_core_node_release(self):
        node = Node('localhost', 55555)
        self.assertEqual(node.udp_ip, ('localhost', 55555))

        self.assertIsInstance(node.udp_sock, socket.socket)
        self.assertFalse(node.udp_sock._closed)
        node.release()
        self.assertTrue(node.udp_sock._closed)
        self.assertIsInstance(node.udp_sock, socket.socket)

    def test_core_node_turn_on_off(self):
        self.assertEqual(1, threading.active_count())
        node = Node('localhost', 55555)
        self.assertEqual(node.udp_ip, ('localhost', 55555))
        self.assertEqual(1, threading.active_count())
        self.assertFalse(node._last_moment.is_set())

        node.appear()
        self.assertFalse(node._last_moment.is_set())
        self.assertEqual(2, threading.active_count())

        self.assertFalse(node.udp_sock._closed)
        node.disappear()
        self.assertTrue(node.udp_sock._closed)
        self.assertEqual(1, threading.active_count())
        self.assertTrue(node._last_moment.is_set())

        # no need to do node.release()
        # Because node.release() where is in node.disappear()
        # close node.udp_sock.

    def test_core_node_status(self):
        node = Node('localhost', 55555)
        self.assertIsInstance(node.udp_sock, socket.socket)
        self.assertEqual(node.udp_ip, ('localhost', 55555))

        status = node.get_status()
        self.assertEqual(status['host'], 'localhost')
        self.assertEqual(status['port'], 55555)

        node.release()

if __name__ == '__main__':
    unittest.main()
