import re, os, io
import sys, shutil
from unittest import mock
import unittest

import umatobi
from umatobi.tests import *
from umatobi.simulator.client import Client

class ClientTests(unittest.TestCase):

    def test_client___init__(self):
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

#   @mock.patch.object('Client', '_make_contact_with')
#   def test_client__consult_watson(self, mock_make_contact_with):
#       mock_make_contact_with.rete
#       watson_office_addr = ('localhost', 11111)
#       num_nodes = 10
#       client = Client(watson_office_addr, num_nodes)
#       client._consult_watson()

#    #  @mock.patch('umatobi.simulator.client.Client.socket.socket')
#     # with unittest.mock.patch('umatobi.simulator.client.Client.socket.socket'):
#       with unittest.mock.patch('umatobi.simulator.client.Client._consult_watson'):
#           client._make_contact_with.assert_called_with()


    @mock.patch('umatobi.simulator.client.socket')
    def test_client__make_contact_with(self, mock_client_sock):
        with unittest.mock.patch('umatobi.simulator.client.socket.socket'):
            watson_office_addr = ('localhost', 11111)
            num_nodes = 10
            client = Client(watson_office_addr, num_nodes)
            self.assertEqual(client.watson_office_addr, watson_office_addr)
            self.assertEqual(client.num_nodes, num_nodes)

            client._make_contact_with()
            mock_client_sock.socket.assert_called_with(umatobi.simulator.client.socket.AF_INET, umatobi.simulator.client.socket.SOCK_STREAM)
            self.assertTrue(client._tcp_sock)
            print(client._tcp_sock)

#   @mock.patch.object(umatobi.simulator.client.Client, '_tcp_sock', 100)
   #@mock.patch('umatobi.simulator.client.Client._watch_mailbox', return_value=b'break down.')
   #@mock.patch('umatobi.simulator.client.Client')
   #def test_client__waits_to_break_down(self, mock_client):
    def test_client__waits_to_break_down(self):
        watson_office_addr = ('localhost', 11111)
        num_nodes = 10
# self._tcp_sock.connect(self.watson_office_addr)
#       mock_client = mock.create_autospec(Client)
#       mock_client._waits_to_break_down()

        client = Client(watson_office_addr, num_nodes)
#       client._tcp_sock = ''
#     # mock.patch.object(client, '_tcp_sock', return_value=100)
#       mock.patch(client, '_tcp_sock', return_value=100)
#       print('client._tcp_sock =', client._tcp_sock)
#       client._make_contact_with()
#       mock.patch.object(client, '_tcp_sock', 100)

#       mock_watch_mailbox.socket.assert_called_with(umatobi.simulator.client.socket.AF_INET, umatobi.simulator.client.socket.SOCK_STREAM)
#       self.assertTrue(client._tcp_sock)
#       client._tcp_sock.connect.assert_called_with(watson_office_addr)

        client._tcp_sock = mock.MagicMock()
        client._tcp_sock.recv.return_value = b'break down.'
        with self.assertLogs('umatobi', level='INFO') as cm:
            client._waits_to_break_down()
      # mock_client._watch_mailbox.assert_called_with(client._tcp_sock)
      # self.assertRegex(cm.output[0], r'^INFO:umatobi:.*\._waits_to_break_down\(\)')
      # self.assertRegex(cm.output[1], r'^INFO:umatobi:.*\._waits_to_break_down\(\), .* got break down from \.*')

    def test_client_start(self):
        watson_office_addr = ('localhost', 0)
        num_nodes = 10

        client = Client(watson_office_addr, num_nodes)

        self.assertEqual(watson_office_addr, client.watson_office_addr)
        self.assertEqual(num_nodes, client.num_nodes)

if __name__ == '__main__':
    unittest.main()
