import re, os, io, importlib
import sys, shutil, sqlite3
from unittest import mock
from unittest.mock import MagicMock
import unittest

import umatobi
from umatobi.tests import *
from umatobi.lib import *
from umatobi.simulator.client import Client
from umatobi.simulator.sql import SQL

class ClientTests(unittest.TestCase):

    @patch('socket.getdefaulttimeout', side_effect=[None, Client.SOCKET_TIMEOUT_SEC])
    @patch('socket.setdefaulttimeout')
    def test_client___init__(self, mock_setdefaulttimeout, mock_getdefaulttimeout):
        watson_office_addr = ('localhost', 10000)

        num_darkness = 7
        remain = Client.NODES_PER_DARKNESS - 1
        num_nodes = Client.NODES_PER_DARKNESS * (num_darkness - 1) + remain

        self.assertIsNone(socket.getdefaulttimeout())
        client = Client(watson_office_addr, num_nodes)
        mock_setdefaulttimeout.assert_called_with(Client.SOCKET_TIMEOUT_SEC)
        self.assertEqual(socket.getdefaulttimeout(), Client.SOCKET_TIMEOUT_SEC)
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

    @mock.patch.object(Client, '_consult_watson', autospec=True)
    @mock.patch.object(Client, '_has_a_lot_on_mind', autospec=True)
    @mock.patch.object(Client, '_confesses_darkness', autospec=True)
    @mock.patch.object(Client, '_waits_to_break_down', autospec=True)
    @mock.patch.object(Client, '_run_a_way', autospec=True)
    @mock.patch.object(Client, '_come_to_a_bad_end', autospec=True)
    @mock.patch.object(Client, '_thank_you_so_much', autospec=True)
    def test_client_start(self, *mocks):
        watson_office_addr = ('localhost', 0)
        num_nodes = 10
        client = Client(watson_office_addr, num_nodes)

      # battle of log
      # print('mocks[0] =', mocks[0])
      # print('type(mocks[0]) =', type(mocks[0]))
      # print('str(mocks[0]) =', str(mocks[0]))
      # print('mocks[0].__dict__ =', mocks[0].__dict__)
      # print('dir(mocks[0]) =', dir(mocks[0]))
      # print('mocks[0].mock._extract_mock_name() =', mocks[0].mock._extract_mock_name())

        for mock in reversed(mocks):
            m = re.search('function (.+) at', str(mock))
            func_name = m[1]
            try:
                mock.assert_called_once_with(client)
            except AssertionError as err:
              # err_msg = f"Expected '{mock.mock._extract_mock_name()}' to be called once. Called 0 times."
                err_msg = f"Expected '{func_name}' to be called once. Called 0 times."
                self.assertEqual(err.args[0], err_msg)
            self.assertEqual(0, mock.call_count)

        client.start()

        for mock in reversed(mocks):
            mock.assert_called_once_with(client)

    @mock.patch.object(Client, '_consult_watson', autospec=True)
    @mock.patch.object(Client, '_has_a_lot_on_mind', autospec=True)
    @mock.patch.object(Client, '_confesses_darkness', autospec=True)
    @mock.patch.object(Client, '_waits_to_break_down', autospec=True)
    @mock.patch.object(Client, '_run_a_way', autospec=True)
    @mock.patch.object(Client, '_come_to_a_bad_end', autospec=True)
    @mock.patch.object(Client, '_thank_you_so_much', autospec=True)
    def test_client_start_by_call_order(self, *mocks):
        watson_office_addr = ('localhost', 11111)
        num_nodes = 10
        master = MagicMock()
        with patch('umatobi.simulator.client.Client', autospec=True, spec_set=True):
            client = Client(watson_office_addr, num_nodes)
        self.assertEqual(client.watson_office_addr, ('localhost', 11111))
        self.assertEqual(client.num_nodes, num_nodes)

        for mock in mocks:
            m = re.search('function (.+) at', str(mock))
            func_name = m[1]
          # print('func_name =', func_name)
            master.attach_mock(mock.mock, func_name)
            try:
                mock.assert_called_once_with(client)
            except AssertionError as err:
                err_msg = f"Expected '{func_name}' to be called once. Called 0 times."
                self.assertEqual(err.args[0], err_msg)
            self.assertEqual(0, mock.call_count)

        client.start()

      # print('mocks[0] == master.method_calls[0] is', mocks[0] == master.method_calls[0])
      # print('mocks[0] == master.method_calls[0] is', master.method_calls[0] == mocks[0])
      # print('mocks =', mocks)
      # print('master.method_calls =', master.method_calls)
        for i, mock in enumerate(reversed(mocks)):
          # self.assertEqual(master.mock_calls[i], mock.mock_calls[0]) # FALSE!
            self.assertEqual(mock.mock_calls[0], master.mock_calls[i]) # TRUE!!
            # ??? different __eq__() ???
        self.assertEqual(len(mocks), len(master.mock_calls))

    @mock.patch('socket.setdefaulttimeout')
    @mock.patch('socket.socket')
    @mock.patch.object(Client, '_init_attrs', return_value={'mock_key': 'mock_value'}, autospec=True)
    def test_client__consult_watson(self, mock_init_attrs, mock_socket, mock_setdefaulttimeout):
        watson_office_addr = ('localhost', 11111)
        num_nodes = 10
        client = Client(watson_office_addr, num_nodes)
        mock_setdefaulttimeout.assert_called_once_with(Client.SOCKET_TIMEOUT_SEC)

        self.assertIsNone(getattr(client, 'client_init_attrs', None))
        client._consult_watson()
        mock_socket.assert_called_once_with(socket.AF_INET,
                                            socket.SOCK_STREAM)
        client._tcp_sock.connect.assert_called_once_with(client.watson_office_addr)
        self.assertEqual(client.client_init_attrs,
                       {'mock_key': 'mock_value'})

    def test_client__has_a_lot_on_mind(self):
        expected_simulation_time = SimulationTime()

        watson_office_addr = ('localhost', 11111)
        num_nodes = 10
        client = Client(watson_office_addr, num_nodes)

        client._hello_watson = mock.MagicMock()
        client._hello_watson.return_value = {
            'client_id': 1,
            'iso8601': expected_simulation_time.get_iso8601(),
            'node_index': 1,
            'log_level': 'INFO',
        }

        reply = client._init_attrs()
        for key, value in reply.items():
            if key == 'client_id':
                key_ = 'id'
            else:
                key_ = key
            if key == 'iso8601':
                self.assertEqual(client.simulation_time, expected_simulation_time)
            else:
                self.assertEqual(getattr(client, key_), reply[key])
        self.assertEqual(getattr(client, 'client_db_path'), get_client_db_path(client.simulation_time, client.id))
        self.assertEqual(getattr(client, 'simulation_schema_path'), get_simulation_schema_path(client.simulation_time))

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
        client.client_db.remove_db()

    def test_client__has_a_lot_on_mind(self):
        expected_simulation_time = SimulationTime()

        watson_office_addr = ('localhost', 11111)
        num_nodes = 10
        client = Client(watson_office_addr, num_nodes)

        client._hello_watson = mock.MagicMock()
        client._hello_watson.return_value = {
            'client_id': 1,
            'iso8601': expected_simulation_time.get_iso8601(),
            'node_index': 1,
            'log_level': 'INFO',
        }

        reply = client._init_attrs()
        for key, value in reply.items():
            if key == 'client_id':
                key_ = 'id'
            else:
                key_ = key
            if key == 'iso8601':
                self.assertEqual(client.simulation_time, expected_simulation_time)
            else:
                self.assertEqual(getattr(client, key_), reply[key])
        self.assertEqual(getattr(client, 'client_db_path'), get_client_db_path(client.simulation_time, client.id))
        self.assertEqual(getattr(client, 'simulation_schema_path'), get_simulation_schema_path(client.simulation_time))

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
        client.client_db.remove_db()

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

    @mock.patch.object(Client, '_make_contact_with', autospec=True)
    def test__make_contact_with(self, mock_contact_with):
        num_nodes = 100
        client = Client(('localhost', 11111), num_nodes)
        self.assertEqual(client.watson_office_addr, ('localhost', 11111))
        self.assertEqual(client.num_nodes, num_nodes)

        client._make_contact_with()
        mock_contact_with.assert_called_with(client)

    @mock.patch.object(socket, 'socket', autospec=True)
    def test__make_contact_with2(self, mock_socket):
        watson_office_addr = ('localhost', 11111)
        num_nodes = 100
        client = Client(watson_office_addr, num_nodes)
        self.assertEqual(client.watson_office_addr, watson_office_addr)
        self.assertEqual(client.num_nodes, num_nodes)

        self.assertIsNone(getattr(client, '_tcp_sock', None))
        client._make_contact_with()
        mock_socket.assert_called_with(socket.AF_INET, socket.SOCK_STREAM)
        client._tcp_sock.connect.assert_called_with(watson_office_addr)
        self.assertIsInstance(client._tcp_sock, type(mock_socket.return_value))

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

    def test_client__make_contact_with2(self):
        watson_office_addr = ('localhost', 11111)
        num_nodes = 100
        client = Client(watson_office_addr, num_nodes)
        self.assertEqual(client.watson_office_addr, watson_office_addr)
        self.assertEqual(client.num_nodes, num_nodes)

        with self.assertLogs('umatobi', level='INFO') as cm:
            with mock.patch.object(socket, 'socket') as mock_socket:
                client._make_contact_with()

        self.assertRegex(cm.output[0], r'^INFO:umatobi:.*\._make_contact_with\(\), .+\.connect\(.+\)')
        mock_socket.assert_called_with(socket.AF_INET, socket.SOCK_STREAM)
        client._tcp_sock.connect.assert_called_with(watson_office_addr)
        self.assertIsInstance(client._tcp_sock, type(mock_socket.return_value))

    @mock.patch.object(socket.socket, 'connect')
    def test_client__mock_connect(self, mock_connect):
        # client._make_contact_with()
        watson_office_addr = ('localhost', 11111)
        num_nodes = 100
        client = Client(watson_office_addr, num_nodes)
        self.assertEqual(client.watson_office_addr, watson_office_addr)
        self.assertEqual(client.num_nodes, num_nodes)

        # socket.socket() return a socket object
        client._make_contact_with()
        self.assertIsInstance(client._tcp_sock, socket.socket)
        mock_connect.assert_called_once_with(watson_office_addr)

        # clean up because we got a real socket object.
        client._tcp_sock.close()

    def test_client__mock_close(self):
        # client._say_good_bye()
        watson_office_addr = ('localhost', 11111)
        num_nodes = 100
        client = Client(watson_office_addr, num_nodes)
        self.assertEqual(client.watson_office_addr, watson_office_addr)
        self.assertEqual(client.num_nodes, num_nodes)

        client._tcp_sock = None
        with self.assertLogs('umatobi', level='INFO') as cm:
            with mock.patch.object(client, '_tcp_sock') as mock__tcp_sock:
                client._say_good_bye()
        mock__tcp_sock.close.assert_called_once_with()
        self.assertRegex(cm.output[0], r'^INFO:umatobi:.*\._say_good_bye\(\), .+\.close\(.+\)')

if __name__ == '__main__':
    unittest.main()
