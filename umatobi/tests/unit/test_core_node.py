# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import os, sys, threading, socket, queue
import unittest

from umatobi.simulator.core.node import Node

class CoreNodeTests(unittest.TestCase):

    def test___init__(self):
        pass

    def test_release(self):
        pass

    def test_sock_make_addr(self):
        node = Node()
        self.assertIsNone(node.udp_sock)

    def test_sock_make_addr1(self):
        node = Node(host='127.0.0.1')
        self.assertIsNone(node.udp_sock)

    def test_sock_make_addr2(self):
        node = Node(host='localhost')
        self.assertIsNone(node.udp_sock)

    def test_sock_make_addr3(self):
        node = Node(port=None)
        self.assertIsNone(node.udp_sock)

    def test_bind_udp_success(self):
        node = Node()
        self.assertIsNone(node.udp_sock)
        self.assertEqual(node.udp_addr, (None, None))
        ret = node.bind_udp('localhost', 4444)
        self.assertTrue(ret)
        self.assertIsInstance(node.udp_sock, socket.socket)
        self.assertEqual(node.udp_addr, ('localhost', 4444))

        node.release()

    def test_bind_udp_doesnt_bind_udp(self):
        pairs_of_host_port = [(None, 4444), ('localhost', None), (None, None)]

        for host, port in pairs_of_host_port:
            node = Node()
            self.assertIsNone(node.udp_sock)
            self.assertEqual(node.udp_addr, (None, None))
            ret = node.bind_udp(host, port)
            self.assertFalse(ret)
            self.assertIsInstance(node.udp_sock, socket.socket)
            node.release()
            self.assertEqual(node.udp_addr, (host, port))

    def test_bind_udp_got_on_the_boundary_port(self):
        for on_the_boundary_port in (1024, 65535):
            node = Node()
            self.assertIsNone(node.udp_sock)
            self.assertEqual(node.udp_addr, (None, None))
            ret = node.bind_udp('localhost', on_the_boundary_port)
            self.assertTrue(ret)
            self.assertIsInstance(node.udp_sock, socket.socket)
            self.assertEqual(node.udp_addr, ('localhost', on_the_boundary_port))

            node.release()

    def test_bind_udp_got_a_sensitive_port(self):
        # Can you bind_udp system ports ?
        for sensitive_port in (1, 1023):
            node = Node()
            self.assertIsNone(node.udp_sock)
            self.assertEqual(node.udp_addr, (None, None))
            with self.subTest(sensitive_port=sensitive_port):
                ret = node.bind_udp('localhost', sensitive_port)
                if ret:
                    # Really !!! You can bind_udp a sensitive port.
                    # Are you root ?
                    # You must study security.
                    # You must open many security holes.
                    self.assertIsInstance(node.udp_sock, socket.socket)
                    node.release()
                    self.assertEqual(node.udp_addr, ('localhost', sensitive_port))
                else:
                    # You cannot bind_udp a sensitive port.
                    # You have a good security policy.
                    self.assertIsInstance(node.udp_sock, socket.socket)
                    node.release()
                    # However port must be set. for debug.
                    self.assertEqual(node.udp_addr, ('localhost', sensitive_port))

    def test_bind_udp_got_out_of_range_port(self):
      # OverflowError: getsockaddrarg: port must be 1-65535.
        for invalid_port in (-1, 65535 + 1):
            node = Node()
            self.assertIsNone(node.udp_sock)
            self.assertEqual(node.udp_addr, (None, None))
            ret = node.bind_udp('localhost', invalid_port)
            self.assertFalse(ret)
            self.assertIsInstance(node.udp_sock, socket.socket)
            node.release()
            self.assertEqual(node.udp_addr, ('localhost', invalid_port))
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
        self.assertEqual(node.udp_addr, ('localhost', 20000))
        self.assertIsInstance(node._last_moment, threading.Event)
        self.assertIsInstance(node._status, dict)

        ret = node.bind_udp(*node.udp_addr)
        self.assertTrue(ret)
        self.assertIsInstance(node.udp_sock, socket.socket)

        node.release()

    def test_core_node_init_fail(self):
        pairs_of_host_port = [('', 10000), ('localhost', None)]
        for host, port in pairs_of_host_port:
            node = Node(host, port)
            self.assertEqual(node.udp_addr, (host, port))
            self.assertIsInstance(node._last_moment, threading.Event)
            self.assertIsInstance(node._status, dict)
            self.assertIsNone(node.udp_sock)

    def test_core_node_release(self):
        node = Node('localhost', 55555)
        self.assertEqual(node.udp_addr, ('localhost', 55555))
        self.assertIsNone(node.udp_sock)

        ret = node.bind_udp(*node.udp_addr)
        self.assertTrue(ret)
        self.assertIsInstance(node.udp_sock, socket.socket)
        self.assertFalse(node.udp_sock._closed)
        node.release()
        self.assertTrue(node.udp_sock._closed)
        self.assertIsInstance(node.udp_sock, socket.socket)

    def test_core_node_turn_on_off(self):
        self.assertEqual(1, threading.active_count())
        node = Node('localhost', 55555)
        self.assertIsNone(node.udp_sock)

        ret = node.bind_udp(*node.udp_addr)
        self.assertTrue(ret)
        self.assertEqual(node.udp_addr, ('localhost', 55555))
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
        self.assertEqual(node.udp_addr, ('localhost', 55555))
        ret = node.bind_udp(*node.udp_addr)
        self.assertTrue(ret)
        self.assertIsInstance(node.udp_sock, socket.socket)

        status = node.get_status()
        self.assertEqual(status['host'], 'localhost')
        self.assertEqual(status['port'], 55555)

        node.release()

if __name__ == '__main__':
    unittest.main()
