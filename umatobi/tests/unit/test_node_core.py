# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import os, sys, threading, socket, queue
import unittest

from umatobi.tests.constants import *
from umatobi.simulator.node.core import NodeCore

class NodeCoreTests(unittest.TestCase):

    def test___init__(self):
        pass

    def test_release(self):
        pass

    def test_sock_make_addr(self):
        node_core = NodeCore()
        self.assertIsNone(node_core.udp_sock)

    def test_sock_make_addr1(self):
        node_core = NodeCore(host='127.0.0.1')
        self.assertIsNone(node_core.udp_sock)

    def test_sock_make_addr2(self):
        node_core = NodeCore(host='localhost')
        self.assertIsNone(node_core.udp_sock)

    def test_sock_make_addr3(self):
        node_core = NodeCore(port=None)
        self.assertIsNone(node_core.udp_sock)

    def test_bind_udp_success(self):
        node_core = NodeCore()
        self.assertIsNone(node_core.udp_sock)
        self.assertEqual(node_core.udp_addr, (None, None))
        ret = node_core.bind_udp('localhost', 4444)
        self.assertTrue(ret)
        self.assertIsInstance(node_core.udp_sock, socket.socket)
        self.assertEqual(node_core.udp_addr, ('localhost', 4444))

        node_core.release()

    def test_bind_udp_doesnt_bind_udp(self):
        pairs_of_host_port = [(None, 4444), ('localhost', None), (None, None)]

        for host, port in pairs_of_host_port:
            node_core = NodeCore()
            self.assertIsNone(node_core.udp_sock)
            self.assertEqual(node_core.udp_addr, (None, None))
            ret = node_core.bind_udp(host, port)
            self.assertFalse(ret)
            self.assertIsInstance(node_core.udp_sock, socket.socket)
            node_core.release()
            self.assertEqual(node_core.udp_addr, (host, port))

    def test_bind_udp_got_on_the_boundary_port(self):
        for on_the_boundary_port in (1024, 65535):
            node_core = NodeCore()
            self.assertIsNone(node_core.udp_sock)
            self.assertEqual(node_core.udp_addr, (None, None))
            ret = node_core.bind_udp('localhost', on_the_boundary_port)
            self.assertTrue(ret)
            self.assertIsInstance(node_core.udp_sock, socket.socket)
            self.assertEqual(node_core.udp_addr, ('localhost', on_the_boundary_port))

            node_core.release()

    def test_bind_udp_got_a_sensitive_port(self):
        # Can you bind_udp system ports ?
        for sensitive_port in (1, 1023):
            node_core = NodeCore()
            self.assertIsNone(node_core.udp_sock)
            self.assertEqual(node_core.udp_addr, (None, None))
            with self.subTest(sensitive_port=sensitive_port):
                ret = node_core.bind_udp('localhost', sensitive_port)
                if ret:
                    # Really !!! You can bind_udp a sensitive port.
                    # Are you root ?
                    # You must study security.
                    # You must open many security holes.
                    self.assertIsInstance(node_core.udp_sock, socket.socket)
                    node_core.release()
                    self.assertEqual(node_core.udp_addr, ('localhost', sensitive_port))
                else:
                    # You cannot bind_udp a sensitive port.
                    # You have a good security policy.
                    self.assertIsInstance(node_core.udp_sock, socket.socket)
                    node_core.release()
                    # However port must be set. for debug.
                    self.assertEqual(node_core.udp_addr, ('localhost', sensitive_port))

    def test_bind_udp_got_out_of_range_port(self):
      # OverflowError: getsockaddrarg: port must be 1-65535.
        for invalid_port in (-1, 65535 + 1):
            node_core = NodeCore()
            self.assertIsNone(node_core.udp_sock)
            self.assertEqual(node_core.udp_addr, (None, None))
            ret = node_core.bind_udp('localhost', invalid_port)
            self.assertFalse(ret)
            self.assertIsInstance(node_core.udp_sock, socket.socket)
            node_core.release()
            self.assertEqual(node_core.udp_addr, ('localhost', invalid_port))
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
        node_core = NodeCore('localhost', 20000)
        self.assertEqual(node_core.udp_addr, ('localhost', 20000))
        self.assertIsInstance(node_core._last_moment, threading.Event)
        self.assertIsInstance(node_core._status, dict)

        ret = node_core.bind_udp(*node_core.udp_addr)
        self.assertTrue(ret)
        self.assertIsInstance(node_core.udp_sock, socket.socket)

        node_core.release()

    def test_core_node_init_fail(self):
        pairs_of_host_port = [('', 10000), ('localhost', None)]
        for host, port in pairs_of_host_port:
            node_core = NodeCore(host, port)
            self.assertEqual(node_core.udp_addr, (host, port))
            self.assertIsInstance(node_core._last_moment, threading.Event)
            self.assertIsInstance(node_core._status, dict)
            self.assertIsNone(node_core.udp_sock)

    def test_core_node_release(self):
        node_core = NodeCore('localhost', 55555)
        self.assertEqual(node_core.udp_addr, ('localhost', 55555))
        self.assertIsNone(node_core.udp_sock)

        ret = node_core.bind_udp(*node_core.udp_addr)
        self.assertTrue(ret)
        self.assertIsInstance(node_core.udp_sock, socket.socket)
        self.assertFalse(node_core.udp_sock._closed)
        node_core.release()
        self.assertTrue(node_core.udp_sock._closed)
        self.assertIsInstance(node_core.udp_sock, socket.socket)

    def test_core_node_turn_on_off(self):
        self.assertEqual(1, threading.active_count())
        node_core = NodeCore('localhost', 55555)
        self.assertIsNone(node_core.udp_sock)

        ret = node_core.bind_udp(*node_core.udp_addr)
        self.assertTrue(ret)
        self.assertEqual(node_core.udp_addr, ('localhost', 55555))
        self.assertEqual(1, threading.active_count())
        self.assertFalse(node_core._last_moment.is_set())

        node_core.appear()
        self.assertFalse(node_core._last_moment.is_set())
        self.assertEqual(2, threading.active_count())

        self.assertFalse(node_core.udp_sock._closed)
        node_core.disappear()
        self.assertTrue(node_core.udp_sock._closed)
        self.assertEqual(1, threading.active_count())
        self.assertTrue(node_core._last_moment.is_set())

        # no need to do node_core.release()
        # Because node_core.release() where is in node_core.disappear()
        # close node_core.udp_sock.

    def test_core_node_status(self):
        node_core = NodeCore('localhost', 55555)
        self.assertEqual(node_core.udp_addr, ('localhost', 55555))
        ret = node_core.bind_udp(*node_core.udp_addr)
        self.assertTrue(ret)
        self.assertIsInstance(node_core.udp_sock, socket.socket)

        status = node_core.get_status()
        self.assertEqual(status['host'], 'localhost')
        self.assertEqual(status['port'], 55555)

        node_core.release()

if __name__ == '__main__':
    unittest.main()
