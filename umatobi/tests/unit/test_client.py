import re, os, io
import sys, shutil, sqlite3
from unittest import mock
import unittest

import umatobi
from umatobi.lib import *
from umatobi.tests import *
from umatobi.simulator.client import Client
from umatobi.simulator.sql import SQL

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


    def test_client__has_a_lot_on_mind(self):
        start_up_orig = make_start_up_orig()
        start_up_time = y15sformat_time(start_up_orig)

        watson_office_addr = ('localhost', 11111)
        num_nodes = 10
        client = Client(watson_office_addr, num_nodes)
        client._hello_watson = mock.MagicMock()
        client._hello_watson.return_value = {
            'client_id': 1,
            'start_up_orig': start_up_orig_to_isoformat(make_start_up_orig()),
            'dir_name': os.path.join(SIMULATION_DIR, start_up_time),
            'node_index': 1,
            'log_level': 'INFO',
        }
        reply = client._init_attrs()
        for key, value in reply.items():
            if key == 'client_id':
                key_ = 'id'
            else:
                key_ = key
            if key == 'start_up_orig':
                self.assertEqual(getattr(client, key_), isoformat_to_start_up_orig(reply[key]))
            else:
                self.assertEqual(getattr(client, key_), reply[key])
        self.assertEqual(getattr(client, 'client_db_path'), os.path.join(client.dir_name, f'client.{client.id}.db'), reply[key])
        self.assertEqual(getattr(client, 'schema_path'), SCHEMA_PATH)

        with self.assertRaises(AttributeError) as cm:
            getattr(client, 'client_db')
        the_exception = cm.exception
        self.assertEqual(the_exception.args[0], "'Client' object has no attribute 'client_db'")

        with self.assertLogs('umatobi', level='INFO') as cm:
            client._has_a_lot_on_mind()
        self.assertRegex(cm.output[0], r'^INFO:umatobi:.*\._makes_growings_table\(\)')
        self.assertIsInstance(getattr(client, 'client_db'), SQL)
        self.assertIn('growings', client.client_db.get_table_names())

        client.client_db.close()

        with self.assertRaises(sqlite3.ProgrammingError) as cm:
            client.client_db.get_table_names()
        the_exception = cm.exception
        self.assertEqual(the_exception.args[0], "Cannot operate on a closed cursor.")

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

    def test_client__waits_to_break_down(self):
        watson_office_addr = ('localhost', 11111)
        num_nodes = 10

        client = Client(watson_office_addr, num_nodes)

        client._tcp_sock = mock.MagicMock()
        client._tcp_sock.recv.return_value = b'break down.'
        with self.assertLogs('umatobi', level='INFO') as cm:
            recved_mail = client._waits_to_break_down()
        self.assertEqual(recved_mail, b'break down.')
        self.assertRegex(cm.output[0], r'^INFO:umatobi:.*\._waits_to_break_down\(\)')

    @mock.patch.object(umatobi.simulator.client.Client, '_watch_mailbox', autospec=True)
    def test_client__waits_to_break_down2(self, mock_client):
        mock_client.return_value = b'break down.'
        watson_office_addr = ('localhost', 11111)
        num_nodes = 10

        client = Client(watson_office_addr, num_nodes)

        client._tcp_sock = mock.MagicMock()
        client._tcp_sock.recv.return_value = b'break down.'
        with self.assertLogs('umatobi', level='INFO') as cm:
            recved_mail = client._waits_to_break_down()
        self.assertRegex(cm.output[0], r'^INFO:umatobi:.*\._waits_to_break_down\(\)')
        self.assertEqual(recved_mail, b'break down.')
      # self.assertRegex(cm.output[1], r'^INFO:umatobi:.*\._waits_to_break_down\(\), .* got break down from \.*')

    def test_client_start(self):
        watson_office_addr = ('localhost', 0)
        num_nodes = 10

        client = Client(watson_office_addr, num_nodes)

        self.assertEqual(watson_office_addr, client.watson_office_addr)
        self.assertEqual(num_nodes, client.num_nodes)

if __name__ == '__main__':
    unittest.main()
