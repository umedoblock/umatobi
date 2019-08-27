import re, os, io
import sys, shutil
import unittest

from umatobi.tests import *
from umatobi.simulator.client import Client

class ClientTests(unittest.TestCase):

    def test_client_init(self):
        watson_office_addr = ('localhost', 10000)

        num_darkness = 7
        remain = Client.NODES_PER_DARKNESS - 1
        num_nodes = Client.NODES_PER_DARKNESS * (num_darkness - 1) + remain
        client = Client(watson_office_addr, num_nodes)
        self.assertEqual(client.watson_office_addr, watson_office_addr)
        self.assertEqual(client.num_nodes, num_nodes)
        self.assertEqual(client.id, -1)
        self.assertEqual(client.nodes_per_darkness, Client.NODES_PER_DARKNESS)
        self.assertEqual(client.node_index, -1)
        self.assertEqual(client.num_darkness, num_darkness)
        self.assertEqual(client.last_darkness_make_nodes, remain)
        self.assertEqual(client.total_created_nodes, 0)
        self.assertEqual(client.darkness_processes, [])
        self.assertFalse(client.leave_there.is_set())
        self.assertEqual(client.timeout_sec, 1)

        num_darkness = 7
        remain = 1
        num_nodes = Client.NODES_PER_DARKNESS * (num_darkness - 1) + remain
        client = Client(watson_office_addr, num_nodes)
        self.assertEqual(client.nodes_per_darkness, Client.NODES_PER_DARKNESS)
        self.assertEqual(client.num_darkness, num_darkness)
        self.assertEqual(client.last_darkness_make_nodes, remain)

        num_darkness = 100
        remain = 0
        num_nodes = Client.NODES_PER_DARKNESS * num_darkness + remain
        client = Client(watson_office_addr, num_nodes)
        self.assertEqual(client.nodes_per_darkness, Client.NODES_PER_DARKNESS)
        self.assertEqual(client.num_darkness, num_darkness)
        self.assertEqual(client.last_darkness_make_nodes, Client.NODES_PER_DARKNESS)

    def test_client_break_down(self):
        watson_office_addr = ('localhost', 0)
        num_nodes = 10

        client = Client(watson_office_addr, num_nodes)

        client._tcp_sock = MockIO(b'break down.')
        with self.assertLogs('umatobi', level='INFO') as cm:
            client._wait_break_down()
        self.assertRegex(cm.output[0], r'^INFO:umatobi:.*\._wait_break_down\(\)')
        self.assertRegex(cm.output[1], r'^INFO:umatobi:.*\._wait_break_down\(\), .* got break down from \.*')

    def test_client_basic(self):
        watson_office_addr = ('localhost', 0)
        num_nodes = 10

        client = Client(watson_office_addr, num_nodes)

        self.assertEqual(watson_office_addr, client.watson_office_addr)
        self.assertEqual(num_nodes, client.num_nodes)

if __name__ == '__main__':
    unittest.main()
