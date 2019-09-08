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
        client._make_contact_with()
        mock_contact_with.assert_called_with(client)

    #  socket(): OK
    # connect(): ?
    @mock.patch.object(socket, 'socket', autospec=True)
    def test_socket2(self, mock_socket):
        client = Client(('localhost', 11111))
        client._make_contact_with()

        mock_socket.assert_called_with(socket.AF_INET, socket.SOCK_STREAM)

  ###  socket(): OK
  ### connect(): ?
  ##@mock.patch.object(socket, 'socket')
  ##@mock.patch('sock.socket', autospec=True)
  ##def test_socket3(self, mock_socket, mock_connect):
  ##    client = Client(('localhost', 11111))
  ##    client._make_contact_with()

  ##    print(client._tcp_sock)
  ##    mock_socket.assert_called_with(socket.AF_INET, socket.SOCK_STREAM)
# ##    mock_socket.return_value.attribute = socket.socket
  ##    client._tcp_sock.connect.assert_called_with(client, 'localhost', 11111)

    #  socket(): OK!
    # connect(): OK
    @mock.patch('sock.socket', autospec=True)
    def test_socket4(self, mock_sock):
      # https://stackoverflow.com/questions/31864168/mocking-a-socket-connection-in-python
        with unittest.mock.patch('sock.socket.socket'):
            watson_office_addr = ('localhost', 11111)
            c = Client(watson_office_addr)
            c._make_contact_with()
            mock_sock.socket.assert_called_with(sock.socket.AF_INET, sock.socket.SOCK_STREAM)
            self.assertTrue(c._tcp_sock)
            c._tcp_sock.connect.assert_called_with(watson_office_addr)

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

    #  socket(): OK
    # connect(): ?
    # no autospec againt test_socket4()
    @mock.patch('sock.socket')
    def test_socket6(self, mock_sock_socket):
        watson_office_addr = ('localhost', 11111)
        c = Client(watson_office_addr)
        c._make_contact_with()
        mock_sock_socket.socket.assert_called_with(sock.socket.AF_INET, sock.socket.SOCK_STREAM)

#   @mock.patch('sock.socket')
#   def test_socket7(self, mock_sock_socket):
    def test_socket7(self):
        watson_office_addr = ('localhost', 11111)
        patcher = mock.patch('sock.Client', autospec=True, watson_office_addr=watson_office_addr)
        mock_client = patcher.start()

        self.assertIsInstance(mock_client, Client)
#       c = Client(watson_office_addr)
#       c = unittest.mock.create_autospec(Client, watson_office_addr)
#       m = Mock(spec=Client)
#       c._make_contact_with()
        mock_client._make_contact_with()
#       mock_client.socket.assert_called_with(sock.socket.AF_INET, sock.socket.SOCK_STREAM)
      # mock_client._tcp_sock.connect.assert_called_with(watson_office_addr)

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
