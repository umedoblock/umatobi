import re, os, io
import sys, shutil
import unittest

from umatobi.tests import *
from umatobi.simulator.client import Client

class ClientTests(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()
        self.assertEqual(num_nodes, client.num_nodes)
