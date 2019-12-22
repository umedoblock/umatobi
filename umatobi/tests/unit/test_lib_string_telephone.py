# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import unittest
from unittest.mock import patch, MagicMock

from umatobi.tests.constants import *
from umatobi.lib.string_telephone import *

class LibTests(unittest.TestCase):

    def test_sock_create_ok(self):
        sock = sock_create('v4', 'tcp')
        self.assertEqual(sock.family, socket.AF_INET)
        self.assertEqual(sock.type, socket.SOCK_STREAM)
        sock.close()
        sock = sock_create('v4', 'udp')
        self.assertEqual(sock.family, socket.AF_INET)
        self.assertEqual(sock.type, socket.SOCK_DGRAM)
        sock.close()
        sock = sock_create('v6', 'tcp')
        self.assertEqual(sock.family, socket.AF_INET6)
        self.assertEqual(sock.type, socket.SOCK_STREAM)
        sock.close()
        sock = sock_create('v6', 'udp')
        self.assertEqual(sock.family, socket.AF_INET6)
        self.assertEqual(sock.type, socket.SOCK_DGRAM)
        sock.close()

        sock = sock_create('V4', 'TCP')
        self.assertEqual(sock.family, socket.AF_INET)
        self.assertEqual(sock.type, socket.SOCK_STREAM)
        sock.close()
        sock = sock_create('V4', 'UDP')
        self.assertEqual(sock.family, socket.AF_INET)
        self.assertEqual(sock.type, socket.SOCK_DGRAM)
        sock.close()
        sock = sock_create('V6', 'TCP')
        self.assertEqual(sock.family, socket.AF_INET6)
        self.assertEqual(sock.type, socket.SOCK_STREAM)
        sock.close()
        sock = sock_create('V6', 'UDP')
        self.assertEqual(sock.family, socket.AF_INET6)
        self.assertEqual(sock.type, socket.SOCK_DGRAM)
        sock.close()

    def test_sock_create_fail(self):
        with self.assertLogs('umatobi', level='ERROR') as cm:
            sock = sock_create('raw', 'tcp')
        self.assertIsNone(sock)
        self.assertRegex(cm.output[0], r'^ERROR:umatobi:"raw" is inappropriate as v4_v6.')

        with self.assertLogs('umatobi', level='ERROR') as cm:
            sock = sock_create('ipsec', 'tcp')
        self.assertIsNone(sock)
        self.assertRegex(cm.output[0], r'^ERROR:umatobi:"ipsec" is inappropriate as v4_v6.')

        with self.assertLogs('umatobi', level='ERROR') as cm:
            sock = sock_create('v4', 'dccp')
        self.assertIsNone(sock)
        self.assertRegex(cm.output[0], r'^ERROR:umatobi:"dccp" is inappropriate as tcp_udp.')

    def test_sock_make_addr(self):
        self.assertEqual(sock_make_addr('localhost', 1222), ('localhost', 1222))
        self.assertEqual(sock_make_addr('127.0.0.1', 1222), ('127.0.0.1', 1222))

        self.assertIsNone(sock_make_addr('localhost', 0))
        self.assertIsNone(sock_make_addr('localhost', None))
        self.assertIsNone(sock_make_addr(None, 1222))
        self.assertIsNone(sock_make_addr(0, 0))
        self.assertIsNone(sock_make_addr(None, None))

    def test_sock_make(self):
        host, port, v4_v6, tcp_udp = 'localhost', 22222, 'v4', 'tcp'
        with patch('umatobi.lib.string_telephone.socket.socket') as mock_socket:
            sock = sock_make(None, host, port, v4_v6, tcp_udp)
        mock_socket.assert_called_with(ADDRESS_FAMILY['v4'],
                                       SOCKET_KIND['tcp'])

    def test_sock_make_retry(self):
        host, port, v4_v6, tcp_udp = 'localhost', 22222, 'v4', 'tcp'
        with patch('umatobi.lib.string_telephone.socket.socket') as mock_socket:
            sock = sock_make(None, host, port, v4_v6, tcp_udp)
        mock_socket.assert_called_with(ADDRESS_FAMILY['v4'],
                                       SOCKET_KIND['tcp'])

        host, port, v4_v6, tcp_udp = 'localhost', 22223, 'v4', 'tcp'
        with patch('umatobi.lib.string_telephone.socket.socket') as mock_socket:
            sock = sock_make(sock, host, port, v4_v6, tcp_udp)
        mock_socket.assert_not_called()

    def test_sock_make_real(self):
        host, port, v4_v6, tcp_udp = 'localhost', 55555, 'v4', 'tcp'
        sock = sock_make(None, host, port, v4_v6, tcp_udp)
        self.assertIsInstance(sock, socket.socket)

        sock.close()

    def test_sock_bind_by_mock(self):
        host, port, v4_v6, tcp_udp = 'localhost', 44444, 'v4', 'tcp'
        addr = host, port
        with patch('umatobi.lib.string_telephone.socket.socket', autospec=socket.socket) as mock_socket:
            sock, addr, result = sock_bind(None, host, port, v4_v6, tcp_udp)
        self.assertIsInstance(sock, socket.socket)
        self.assertEqual(addr, (host, port))
        self.assertTrue(result)
        mock_socket.assert_called_with(ADDRESS_FAMILY['v4'],
                                       SOCKET_KIND['tcp'])
        sock.bind.assert_called_with(addr)

    def test_sock_bind_real(self):
        host, port, v4_v6, tcp_udp = 'localhost', 44444, 'v4', 'tcp'
        expected_ip = socket.gethostbyname(host)
        # expected_ip = \
        #        socket.getaddrinfo(host, port,
        #                           ADDRESS_FAMILY[v4_v6], SOCKET_KIND['tcp'])
        # (family, type, proto, canonname, sockaddr)

        sock, addr, result = sock_bind(None, host, port, v4_v6, tcp_udp)
        self.assertIsInstance(sock, socket.socket)
        self.assertEqual(addr, (host, port))
        self.assertTrue(result)

        got_ip, got_port = sock.getsockname()
        sock.close()

        self.assertEqual(got_ip, expected_ip)
        self.assertEqual(got_port, port)

    def test_sock_bind_fail1(self):
        host, port, v4_v6, tcp_udp = None, 44444, 'v4', 'tcp'

        sock, addr, result = sock_bind(None, host, port, v4_v6, tcp_udp)
        self.assertIsInstance(sock, socket.socket)
        self.assertEqual(addr, (host, port))
        self.assertFalse(result)

        sock.close()

    def test_sock_bind_fail2(self):
        host, port, v4_v6, tcp_udp = 'localhost', None, 'v4', 'tcp'

        sock, addr, result = sock_bind(None, host, port, v4_v6, tcp_udp)
        self.assertIsInstance(sock, socket.socket)
        self.assertEqual(addr, (host, port))
        self.assertFalse(result)

        sock.close()

    def test_sock_bind_fail3(self):
        host, port, v4_v6, tcp_udp = 'localhost', 44444, 'v444444', 'tcp'

        sock, addr, result = sock_bind(None, host, port, v4_v6, tcp_udp)
        self.assertIsNone(sock)
        self.assertEqual(addr, (host, port))
        self.assertFalse(result)

    def test_sock_bind_fail4(self):
        host, port, v4_v6, tcp_udp = 'localhost', 44444, 'v4', 'tcppppp'

        sock, addr, result = sock_bind(None, host, port, v4_v6, tcp_udp)
        self.assertIsNone(sock)
        self.assertEqual(addr, (host, port))
        self.assertFalse(result)

    def test_sock_bind_fail_by_socket_timeout_error(self):
        host, port, v4_v6, tcp_udp = 'localhost', 44444, 'v4', 'tcp'

        with patch('umatobi.lib.string_telephone.socket.socket.bind',
                    side_effect=socket.timeout) as mock_bind:
            sock, addr, result = sock_bind(None, host, port, v4_v6, tcp_udp)
        self.assertIsInstance(sock, socket.socket)
        self.assertEqual(addr, (host, port))
        self.assertFalse(result)

        mock_bind.assert_called_with((host, port))

        sock.close()

    def test_sock_connect(self):
        host, port, v4_v6, tcp_udp = 'localhost', 44444, 'v4', 'tcp'
        addr = host, port
        with patch('umatobi.lib.string_telephone.socket.socket') as mock_socket:
            sock = sock_connect(None, host, port, v4_v6, tcp_udp)
        mock_socket.assert_called_with(ADDRESS_FAMILY['v4'],
                                       SOCKET_KIND['tcp'])
        self.assertIsInstance(sock, MagicMock)
        sock.connect.assert_called_with(addr)

    def test_sock_connect_fail1(self):
        host, port, v4_v6, tcp_udp = None, 44444, 'v4', 'tcp'
        addr = host, port
        with patch('umatobi.lib.string_telephone.socket.socket') as mock_socket:
            self.assertIsNone(sock_connect(None, host, port, v4_v6, tcp_udp))
        mock_socket.assert_not_called()

    def test_sock_connect_fail2(self):
        host, port, v4_v6, tcp_udp = 'localhost', None, 'v4', 'tcp'
        addr = host, port
        with patch('umatobi.lib.string_telephone.socket.socket') as mock_socket:
            self.assertIsNone(sock_connect(None, host, port, v4_v6, tcp_udp))
        mock_socket.assert_not_called()

    def test_sock_connect_fail3(self):
        host, port, v4_v6, tcp_udp = 'localhost', 44444, 'v444444', 'tcp'
        addr = host, port
        sock = sock_connect(None, host, port, v4_v6, tcp_udp)
        self.assertIsNone(sock)

    def test_sock_connect_fail4(self):
        host, port, v4_v6, tcp_udp = 'localhost', 44444, 'v4', 'tcppppp'
        addr = host, port
        sock = sock_connect(None, host, port, v4_v6, tcp_udp)
        self.assertIsNone(sock)

    def test_sock_connect_fail_by_refused(self):
        host, port, v4_v6, tcp_udp = 'localhost', 65535, 'v4', 'tcp'

        sock = sock_connect(None, host, port, v4_v6, tcp_udp)
        self.assertIsInstance(sock, socket.socket)
        sock.close()

    def test_sock_connect_fail_by_refused2(self):
        host, port, v4_v6, tcp_udp = 'localhost', 65535, 'v4', 'tcp'

        cre = ConnectionRefusedError(61, 'Connection refused')
        with patch('umatobi.lib.string_telephone.socket.socket.connect',
                    side_effect=cre) as mock_connect:
            sock = sock_connect(None, host, port, v4_v6, tcp_udp)
        mock_connect.assert_called_with((host, port))
        self.assertIsInstance(sock, socket.socket)
        sock.close()

    def test_sock_connect_fail_by_refused3(self):
        host, port, v4_v6, tcp_udp = 'localhost', 65535, 'v4', 'tcp'

        cre = ConnectionRefusedError(6666666666, 'Connection refused')
        with patch('umatobi.lib.string_telephone.socket.socket.connect',
                    side_effect=cre) as mock_connect:
            sock = sock_connect(None, host, port, v4_v6, tcp_udp)
        mock_connect.assert_called_with((host, port))
        self.assertIsInstance(sock, socket.socket)
        sock.close()

    def test_sock_connect_fail_by_refused4(self):
        host, port, v4_v6, tcp_udp = 'localhost', 65535, 'v4', 'tcp'

        cre = ConnectionRefusedError(61, 'unexpected message')
        with patch('umatobi.lib.string_telephone.socket.socket.connect',
                    side_effect=cre) as mock_connect:
            try:
                sock = sock_connect(None, host, port, v4_v6, tcp_udp)
            except ConnectionRefusedError as err:
                self.assertEqual(err.args[1], 'unexpected message')

        mock_connect.assert_called_with((host, port))

    def test_sock_send_ok_tcp(self):
        with patch('umatobi.lib.string_telephone.socket', spec_set=True):
            tcp_sock = sock_create('v4', 'tcp')

        send_data = b'send mocked data'
        result = sock_send(tcp_sock, send_data)
        tcp_sock.sendall.assert_called_once_with(send_data)
        self.assertTrue(result)

        with patch('umatobi.lib.string_telephone.socket', spec_set=True) as mock_sock:
            tcp_sock = sock_create('v4', 'tcp')
        mock_sock.socket.assert_called_once_with(ADDRESS_FAMILY['v4'],
                                                 SOCKET_KIND['tcp'])

    def test_sock_sendall_fail_by_socket_timeout(self):
        with patch('umatobi.lib.string_telephone.socket.socket', autospec=socket.socket):
            tcp_sock = sock_create('v4', 'tcp')

        with self.assertLogs('umatobi', level='INFO') as cm:
            with patch.object(tcp_sock, 'sendall',
                              side_effect=socket.timeout) as mock_sendall:
                result = sock_send(tcp_sock, b'timeout!')
        self.assertEqual(cm.output[0],
            fr'INFO:umatobi:{tcp_sock}.sendall() got timeout.')
        self.assertFalse(result)
        mock_sendall.assert_called_with(b'timeout!')

        tcp_sock.close()

    def test_sock_recv_ok_tcp(self):
        with patch('umatobi.lib.string_telephone.socket', autospec=True, spec_set=True):
            tcp_sock = sock_create('v4', 'tcp')
        self.assertIsInstance(tcp_sock, socket.socket)

        expected_recv = b'recv mocked data'
        with patch.object(tcp_sock, 'recv', return_value=expected_recv) as mock_sock:
            recved_data = sock_recv(tcp_sock, 1024)
        self.assertEqual(recved_data, expected_recv)

        with patch.object(tcp_sock, 'recv', side_effect=socket.timeout):
            recved_data = sock_recv(tcp_sock, 1024)
        self.assertIsNone(recved_data)

    def test_sock_recv_ok_udp(self):
        with patch('umatobi.lib.string_telephone.socket', autospec=True, spec_set=True):
            udp_sock = sock_create('v4', 'udp')
        self.assertIsInstance(udp_sock, socket.socket)

        expected_recv = b'recv mocked data'
        with patch.object(udp_sock, 'recv', return_value=expected_recv) as mock_sock:
            recved_data = sock_recv(udp_sock, 1024)
        self.assertEqual(recved_data, expected_recv)

    def test_sock_recv_fail_by_socket_timeout(self):
        with patch('umatobi.lib.string_telephone.socket.socket', autospec=socket.socket):
            tcp_sock = sock_create('v4', 'tcp')

        with self.assertLogs('umatobi', level='INFO') as cm:
            with patch.object(tcp_sock, 'recv', side_effect=socket.timeout):
                recved_data = sock_recv(tcp_sock, 1024)
        self.assertEqual(cm.output[0],
            fr'INFO:umatobi:{tcp_sock}.recv(1024) got timeout.')
        self.assertIsNone(recved_data)

        tcp_sock.close()

    def test_addr_on_localhost(self):
        addr = ('localhost', 8888)
        with self.assertLogs('umatobi', level='INFO') as cm:
            self.assertTrue(addr_on_localhost(addr))
        self.assertEqual(cm.output[0], f'INFO:umatobi:addr={addr} is on localhost.')

        addr = ('127.0.0.1', 8888)
        with self.assertLogs('umatobi', level='INFO') as cm:
            self.assertTrue(addr_on_localhost(addr))
        self.assertEqual(cm.output[0], f'INFO:umatobi:addr={addr} is on localhost.')

    def test_addr_on_localhost_fail(self):
        addr = ('umatobi.com', 8888)
        with self.assertLogs('umatobi', level='INFO') as cm:
            self.assertFalse(addr_on_localhost(addr))
        self.assertEqual(cm.output[0], f'INFO:umatobi:addr={addr} is not on localhost.')

        addr = ('192.168.1.1', 8888)
        with self.assertLogs('umatobi', level='INFO') as cm:
            self.assertFalse(addr_on_localhost(addr))
        self.assertEqual(cm.output[0], f'INFO:umatobi:addr={addr} is not on localhost.')

    def test_get_host_port(self):
        host_port = 'localhost:8888'
        self.assertEqual(get_host_port(host_port), ('localhost', 8888))
        host_port = '192.168.1.1:9999'
        self.assertEqual(get_host_port(host_port), ('192.168.1.1', 9999))

class LibStringTelephoneTests(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()
