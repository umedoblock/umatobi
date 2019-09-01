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
