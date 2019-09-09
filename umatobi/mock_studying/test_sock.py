# Thanks Naftuli Kay
# https://www.toptal.com/python/an-introduction-to-mocking-in-python

import socket
from unittest import mock
import unittest

import sock
from sock import Client

class ClientTestCase(unittest.TestCase):
    @mock.patch.object(Client, '_make_contact_with', autospec=True)
    def test_socket(self, mock_contact_with):
        client = Client(('localhost', 11111))
        self.assertEqual(client.watson_office_addr, ('localhost', 11111))

        client._make_contact_with()
        mock_contact_with.assert_called_with(client)
        # ...

    @mock.patch.object(Client, '_make_contact_with')
    def test_socket2(self, mock_contact_with):
        client = Client(('localhost', 11111))
        self.assertEqual(client.watson_office_addr, ('localhost', 11111))

        client._make_contact_with()
        mock_contact_with.assert_called_with()
        mock_contact_with.assert_called_with(client)
        mock_contact_with.assert_called_with(None)
        # ??? Pay attention to autospec=True or not !!!

    @mock.patch.object(socket, 'socket', autospec=True)
    def test_socket2(self, mock_socket):
        watson_office_addr = ('localhost', 11111)
        client = Client(watson_office_addr)
        self.assertEqual(client.watson_office_addr, watson_office_addr)

        client._make_contact_with()
        mock_socket.assert_called_with(socket.AF_INET, socket.SOCK_STREAM)
        client._tcp_sock.connect.assert_called_with(watson_office_addr)
        self.assertIsInstance(client._tcp_sock, type(mock_socket.return_value))

    # use with statement
    def test_socket4(self):
        watson_office_addr = ('localhost', 11111)
        with mock.patch.object(sock.socket, 'socket') as mock_socket:
            c = Client(watson_office_addr)
            self.assertEqual(c.watson_office_addr, watson_office_addr)

            c._make_contact_with()
            mock_socket.assert_called_with(socket.AF_INET, socket.SOCK_STREAM)
            c._tcp_sock.connect.assert_called_with(watson_office_addr)
            self.assertIsInstance(c._tcp_sock, type(mock_socket.return_value))

    @mock.patch.object(sock.socket.socket, 'connect')
    def test_socket5(self, mock_connect):
        watson_office_addr = ('localhost', 11111)
        c = Client(watson_office_addr)
        self.assertEqual(c.watson_office_addr, watson_office_addr)

        # socket.socket() return a socket object
        c._make_contact_with()
        self.assertIsInstance(c._tcp_sock, sock.socket.socket)
        mock_connect.assert_called_once_with(watson_office_addr)

        # clean up because we got a real socket object.
        c._tcp_sock.close()

    def test_socket7(self):
        watson_office_addr = ('localhost', 11111)
        patcher = mock.patch('sock.Client', autospec=True, watson_office_addr=watson_office_addr)
        mock_client = patcher.start()
        self.assertIsInstance(mock_client, Client)
        self.assertEqual(mock_client.watson_office_addr, watson_office_addr)

        mock_client._make_contact_with_raise()
        mock_client._make_contact_with_raise.assert_called_with()
        # absolutely no call client._make_contact_with_raise()
        # so difficult to understand it !

        mock_client = patcher.stop()
