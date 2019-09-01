import socket
from unittest import mock
import unittest

from sock import Client

class ClientTestCase(unittest.TestCase):
    @mock.patch.object(Client, '_make_contact_with', autospec=True)
    def test_socket(self, mock_contact_with):
        client = Client(('localhost', 11111))
        client._make_contact_with()
        mock_contact_with.assert_called_with(client)

    @mock.patch.object(socket, 'socket', autospec=True)
#   @mock.patch('sock.socket')
    def test_socket2(self, mock_socket):
        client = Client(('localhost', 11111))
        client._make_contact_with()

        mock_socket.assert_called_with(socket.AF_INET, socket.SOCK_STREAM)
      # mock_contact_with.assert_called_with('localhost', 11111)

#   @mock.patch.object(socket.socket, 'connect', autospec=True)
#   @mock.patch.object(socket, 'socket', spec=socket)
#   def test_socket3(self, mock_socket, mock_socket_connect):
#       client = Client(('localhost', 11111))
#       client._make_contact_with()

#       print(client._tcp_sock)
#       mock_socket.assert_called_with(socket.AF_INET, socket.SOCK_STREAM)
#       mock_socket.return_value.attribute = socket.socket
#       mock_socket_connect.assert_called_with(client._tcp_sock, 'localhost', 11111)

  # @mock.patch('sock.socket.socket')

    def test_socket4(self):
      # https://stackoverflow.com/questions/31864168/mocking-a-socket-connection-in-python
        with unittest.mock.patch('sock.socket.socket'):
            watson_office_addr = ('localhost', 11111)
            c = Client(watson_office_addr)
            c._make_contact_with()
            c._tcp_sock.connect.assert_called_with(watson_office_addr)
