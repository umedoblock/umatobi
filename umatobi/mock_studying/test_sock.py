import socket
from unittest import mock
import unittest

import sock
from sock import Client

class ClientTestCase(unittest.TestCase):
    #  socket(): ?
    # connect(): ?
    @mock.patch.object(Client, '_make_contact_with', autospec=True)
    def test_socket(self, mock_contact_with):
        client = Client(('localhost', 11111))
        self.assertEqual(client.watson_office_addr, ('localhost', 11111))

        client._make_contact_with()
        mock_contact_with.assert_called_with(client)
        # ...

    #  socket(): OK
    # connect(): OK
    @mock.patch.object(socket, 'socket', autospec=True)
    def test_socket2(self, mock_socket):
        watson_office_addr = ('localhost', 11111)
        client = Client(watson_office_addr)
        self.assertEqual(client.watson_office_addr, watson_office_addr)

        client._make_contact_with()
        mock_socket.assert_called_with(socket.AF_INET, socket.SOCK_STREAM)
        client._tcp_sock.connect.assert_called_with(watson_office_addr)
        self.assertIsInstance(client._tcp_sock, type(mock_socket.return_value))

    #  socket(): OK!
    # connect(): OK
    @mock.patch('sock.socket', autospec=True)
    def test_socket4(self, mock_sock):
      # https://stackoverflow.com/questions/31864168/mocking-a-socket-connection-in-python
        watson_office_addr = ('localhost', 11111)
        c = Client(watson_office_addr)
        self.assertEqual(c.watson_office_addr, watson_office_addr)

        c._make_contact_with()
        mock_sock.socket.assert_called_with(sock.socket.AF_INET, sock.socket.SOCK_STREAM)
        self.assertTrue(c._tcp_sock)
        c._tcp_sock.connect.assert_called_with(watson_office_addr)
        self.assertIsInstance(c._tcp_sock, type(mock_sock.socket.return_value))
        # This test share view point with test_socket2().
        # delete with statement...

    #  socket(): OK
    # connect(): OK
    # no with statement againt test_socket4()
    @mock.patch('sock.socket', autospec=True)
    def test_socket5(self, mock_sock_socket):
        watson_office_addr = ('localhost', 11111)
        c = Client(watson_office_addr)

        c._make_contact_with()
        mock_sock_socket.socket.assert_called_with(sock.socket.AF_INET, sock.socket.SOCK_STREAM)
        c._tcp_sock.connect.assert_called_once_with(watson_office_addr)
        # equal to test_socket4() ...

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

    def test_request(self):
        import urllib
        from urllib import request

        patcher = mock.patch('urllib.request', autospec=True)
        mock_request = patcher.start()

        self.assertIs(urllib.request, mock_request)
        self.assertIsInstance(mock_request.Request, request.Request)
        req = mock_request.Request('foo')
       #print('req =', req)
        self.assertIsInstance(req, request.Request)

        req.add_header('spam', 'eggs')
        req.add_header.assert_called_with('spam', 'eggs')

        patcher.stop()
