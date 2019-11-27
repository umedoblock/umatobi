# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import os, sys, re, shutil, socket
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
from datetime import datetime, timedelta

import yaml
from umatobi.tests import *
from umatobi.log import make_logger
from umatobi.lib import *
from umatobi.simulator.core.key import Key
from umatobi.simulator.sql import SQL

class LibTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.start_up_orig = SimulationTime()
        set_simulation_schema(cls.start_up_orig)

        # yaml_path = 'tests/assets/test.yaml'
        cls.YAML = load_yaml(replace_atat_n(''))

        cls.test_db_path = TESTS_DB_PATH
        cls.test_yaml_path = replace_atat_n('')
        cls.test_schema_path = TESTS_SCHEMA_PATH
       #print('cls.test_db_path =', cls.test_db_path)
       #print('cls.test_yaml_path =', cls.test_yaml_path)
       #print('cls.test_schema_path =', cls.test_schema_path)
        cls.test_db = SQL(db_path=cls.test_db_path,
                          schema_path=cls.test_schema_path)
        cls.test_db.create_db()

    @classmethod
    def tearDownClass(cls):
        cls.YAML = ''

        cls.test_db.close()
        cls.test_db.remove_db()

    def assert_client_db_path(self, client_db_path):
        self.assertRegex(client_db_path, RE_CLIENT_N_DB)
        self.assertNotRegex(client_db_path, ATAT_N)

    def assert_simulation_schema_path(self, inspected_path):
        self.assert_simulation_dir_path(inspected_path)
        self.assertRegex(inspected_path, f"{SIMULATION_SCHEMA}$")

    def assert_simulation_dir_path(self, dir_path):
        self.assertTrue(os.path.isdir(os.path.dirname(dir_path)))
        self.assertNotRegex(dir_path,
                            ATAT_SIMULATION_TIME)
        self.assertRegex(dir_path, RE_Y15S)

    def setUp(self):
        self.simulation_dir_path = \
            os.path.join(SIMULATION_ROOT_PATH, SIMULATION_DIR_PATH)
        self.simulation_time = SimulationTime()

    def tearDown(self):
        shutil.rmtree(os.path.dirname(get_master_palm_path(self.simulation_time)), ignore_errors=True)

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
        with patch('umatobi.lib.socket.socket') as mock_socket:
            sock = sock_make(None, host, port, v4_v6, tcp_udp)
        mock_socket.assert_called_with(ADDRESS_FAMILY['v4'],
                                       SOCKET_KIND['tcp'])

    def test_sock_make_retry(self):
        host, port, v4_v6, tcp_udp = 'localhost', 22222, 'v4', 'tcp'
        with patch('umatobi.lib.socket.socket') as mock_socket:
            sock = sock_make(None, host, port, v4_v6, tcp_udp)
        mock_socket.assert_called_with(ADDRESS_FAMILY['v4'],
                                       SOCKET_KIND['tcp'])

        host, port, v4_v6, tcp_udp = 'localhost', 22223, 'v4', 'tcp'
        with patch('umatobi.lib.socket.socket') as mock_socket:
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
        with patch('umatobi.lib.socket.socket', autospec=socket.socket) as mock_socket:
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

    def test_sock_bind_fail_by_socket_timeout_error(self):
        host, port, v4_v6, tcp_udp = 'localhost', 44444, 'v4', 'tcp'

        with patch('umatobi.lib.socket.socket.bind',
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
        with patch('umatobi.lib.socket.socket') as mock_socket:
            sock = sock_connect(None, host, port, v4_v6, tcp_udp)
        mock_socket.assert_called_with(ADDRESS_FAMILY['v4'],
                                       SOCKET_KIND['tcp'])
        self.assertIsInstance(sock, MagicMock)
        sock.connect.assert_called_with(addr)

    def test_sock_connect_fail_by_refused(self):
        host, port, v4_v6, tcp_udp = 'localhost', 65535, 'v4', 'tcp'

        sock = sock_connect(None, host, port, v4_v6, tcp_udp)
        self.assertIsInstance(sock, socket.socket)
        sock.close()

    def test_sock_connect_fail_by_refused2(self):
        host, port, v4_v6, tcp_udp = 'localhost', 65535, 'v4', 'tcp'

        cre = ConnectionRefusedError(61, 'Connection refused')
        with patch('umatobi.lib.socket.socket.connect',
                    side_effect=cre) as mock_connect:
            sock = sock_connect(None, host, port, v4_v6, tcp_udp)
        mock_connect.assert_called_with((host, port))
        self.assertIsInstance(sock, socket.socket)
        sock.close()

    def test_sock_connect_fail_by_refused3(self):
        host, port, v4_v6, tcp_udp = 'localhost', 65535, 'v4', 'tcp'

        cre = ConnectionRefusedError(6666666666, 'Connection refused')
        with patch('umatobi.lib.socket.socket.connect',
                    side_effect=cre) as mock_connect:
            sock = sock_connect(None, host, port, v4_v6, tcp_udp)
        mock_connect.assert_called_with((host, port))
        self.assertIsInstance(sock, socket.socket)
        sock.close()

    def test_sock_connect_fail_by_refused4(self):
        host, port, v4_v6, tcp_udp = 'localhost', 65535, 'v4', 'tcp'

        cre = ConnectionRefusedError(61, 'unexpected message')
        with patch('umatobi.lib.socket.socket.connect',
                    side_effect=cre) as mock_connect:
            try:
                sock = sock_connect(None, host, port, v4_v6, tcp_udp)
            except ConnectionRefusedError as err:
                self.assertEqual(err.args[1], 'unexpected message')

        mock_connect.assert_called_with((host, port))

    def test_sock_send_ok_tcp(self):
        with patch('umatobi.lib.socket', spec_set=True):
            tcp_sock = sock_create('v4', 'tcp')

        send_data = b'send mocked data'
        result = sock_send(tcp_sock, send_data)
        tcp_sock.sendall.assert_called_once_with(send_data)
        self.assertTrue(result)

        with patch('umatobi.lib.socket', spec_set=True) as mock_sock:
            tcp_sock = sock_create('v4', 'tcp')
        mock_sock.socket.assert_called_once_with(ADDRESS_FAMILY['v4'],
                                                 SOCKET_KIND['tcp'])

    def test_sock_sendall_fail_by_socket_timeout(self):
        with patch('umatobi.lib.socket.socket', autospec=socket.socket):
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
        with patch('umatobi.lib.socket', autospec=True, spec_set=True):
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
        with patch('umatobi.lib.socket', autospec=True, spec_set=True):
            udp_sock = sock_create('v4', 'udp')
        self.assertIsInstance(udp_sock, socket.socket)

        expected_recv = b'recv mocked data'
        with patch.object(udp_sock, 'recv', return_value=expected_recv) as mock_sock:
            recved_data = sock_recv(udp_sock, 1024)
        self.assertEqual(recved_data, expected_recv)

    def test_sock_recv_fail_by_socket_timeout(self):
        with patch('umatobi.lib.socket.socket', autospec=socket.socket):
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

    def test_make_fixture(self):
        expected_qwer = \
            ({
                'id': 4,
                'now_iso8601': '2011-12-22T11:11:44.901234',
                'addr': '127.0.0.1:22222',
                'key': b'\xaa' * Key.KEY_OCTETS,
                'status': 'inactive'
            },)

        yaml_path = replace_atat_n('')
      # print('yaml_path =', yaml_path)
        schema_parser, table_name, qwer = make_fixture(yaml_path, 'qwer')

        self.assertEqual(schema_parser.schema_path,
                         os.path.join(TESTS_ASSETS_DIR,
                             '../../simulator/simulation.schema'))
        self.assertEqual(table_name, 'nodes')
        self.assertEqual(qwer, (expected_qwer))

    def test_make_fixture_normal(self):
        expected_id_is_null = (
            {
            'id': 111,
            'val_null': None,
            'val_integer': 10,
            'val_real': 7.5,
            'val_text': 'test area',
            'val_blob': b'base64 encoded blob',
        },)

        schema_parser, table_name, fixture_id_is_null = \
                make_fixture(replace_atat_n('_schema'),
                            'test_normal')
        self.assertEqual(table_name, 'test_table')
        self.assertSequenceEqual(fixture_id_is_null, expected_id_is_null)

    def test_make_fixture_id_is_null(self):
        expected_id_is_null = ({
            'id': None,
            'val_null': None,
            'val_integer': 0,
            'val_real': 0.0,
            'val_text': 'id is null',
            'val_blob': b'id is null',
        },)

        schema_parser, table_name, fixture_id_is_null = \
                make_fixture(replace_atat_n('_schema'),
                            'test_id_is_null')
        self.assertEqual(schema_parser.schema_path, os.path.join(TESTS_ASSETS_DIR, 'test.schema'))
        self.assertEqual(table_name, 'test_table')
        self.assertEqual(fixture_id_is_null, expected_id_is_null)

    def test_make_fixture_double(self):
        expected_double = ( {
            'id': 0,
            'val_null':    None,
            'val_integer': 0,
            'val_real':    0.0,
            'val_text':    'id is zero',
            'val_blob':    b'id is zero',
        }, {
            'id': 1,
            'val_null':    None,
            'val_integer': 1,
            'val_real':    1.0,
            'val_text':    'id is one',
            'val_blob':    b'id is one',
        } )
        schema_parser, table_name, double = \
                make_fixture(replace_atat_n('_schema'),
                            'test_double')
        self.assertEqual(schema_parser.schema_path, os.path.join(TESTS_ASSETS_DIR, 'test.schema'))
        self.assertEqual(table_name, 'test_table')
        self.assertEqual(double, expected_double)

    def test_inserts_fixture_multiple_times(self):
        expected_multiple = ( {
            'id': 0,
            'val_null':    None,
            'val_integer': 0,
            'val_real':    0.0,
            'val_text':    'multiple inserts 0',
            'val_blob':    b'multiple inserts 0',
            'now':          '2002-11-02T23:22:00.000',
            'elapsed_time': 100.000,
            'iso8601':      '2002-11-02T23:22:00.000000',
        }, {
            'id': 1,
            'val_null':    None,
            'val_integer': 1,
            'val_real':    1.1,
            'val_text':    'multiple inserts 1',
            'val_blob':    b'multiple inserts 1',
            'now':          '2112-11-12T23:22:11.111',
            'elapsed_time': 111.111,
            'iso8601':      '2112-11-12T23:22:11.111111',
        } )

        db = LibTests.test_db
        for i in range(2):
            schema_parser, table_name, fixture = \
                    inserts_fixture(db, LibTests.test_yaml_path,
                                f'test_multiple_inserts_{i}')
            self.assertEqual(schema_parser.schema_path, os.path.join(TESTS_ASSETS_DIR, 'test.schema'))
            self.assertEqual(table_name, 'test_table')
            self.assertEqual(fixture, (expected_multiple[i],))

            rows = db.select('test_table')
           #print('rows =', rows)
           #print('rows[0] =', rows[0])
           #print('tuple(rows[0]) =', tuple(rows[0]))
            expected_tuple = [tuple(em.values()) for em in expected_multiple[:i+1]]
            self.assertEqual(len(rows), len(expected_multiple[:i+1]))
            inspect_tuple = [tuple(row) for row in rows]
           #print(' inspect_tuple =', inspect_tuple)
           #print('expected_tuple =', expected_tuple)
            self.assertEqual(inspect_tuple, expected_tuple)

    def test_converter_blob(self):
      # $ echo -n 'converter_blob' | python3 -m base64 -e -
      # Y29udmVydGVyX2Jsb2I=
      # $ echo -n '' | python3 -m base64 -e -

      # $ echo -n 'a b c' | python3 -m base64 -e -
      # YSBiIGM=
        self.assertEqual(converter_blob(''), b'')
        self.assertEqual(converter_blob('Y29udmVydGVyX2Jsb2I='), b'converter_blob')
        self.assertEqual(converter_blob('YSBiIGM='), b'a b c')

    def test_converter_real(self):
        self.assertEqual(converter_real('0.0'), 0.0)
        self.assertEqual(converter_real('100.8'), 100.8)
        self.assertIsNone(converter_real('null'))
        self.assertIsNone(converter_real('NULL'))
        self.assertIsNone(converter_real('Null'))
        self.assertIsNone(converter_real('None'))
        self.assertIsNone(converter_real('none'))
        self.assertIsNone(converter_real('NONE'))

    def test_converter_integer(self):
        self.assertEqual(converter_integer('0'), 0)
        self.assertEqual(converter_integer('100'), 100)
        self.assertIsNone(converter_integer('null'))
        self.assertIsNone(converter_integer('NULL'))
        self.assertIsNone(converter_integer('Null'))
        self.assertIsNone(converter_integer('None'))
        self.assertIsNone(converter_integer('none'))
        self.assertIsNone(converter_integer('NONE'))

    def test_converter_text(self):
        self.assertEqual(converter_text(''), '')
        self.assertEqual(converter_text('converter_text'), 'converter_text')

    def test_converter_null(self):
        self.assertIsNone(converter_null(0))
        self.assertIsNone(converter_null(1))
        self.assertIsNone(converter_null((1, 2, 3)))
        self.assertIsNone(converter_null('any arg'))

    def test_some_PATHs(self):
        self.assertRegex(UMATOBI_ROOT_PATH, f"^{TESTS_PATH}")
        self.assertRegex(SIMULATION_ROOT_PATH, f"^{TESTS_PATH}")

        self.assertRegex(SIMULATION_DIR_PATH, r'/@@SIMULATION_TIME@@$')
        self.assertRegex(SIMULATION_SCHEMA_PATH, r'/tests/')

    def test_get_client_db_path(self):
        client_id = 8
        client_db_path = get_client_db_path(self.simulation_time,
                                            client_id)
        self.assert_client_db_path(client_db_path)

        client_id = 88888
        client_db_path = get_client_db_path(self.simulation_time,
                                            client_id)
        self.assert_client_db_path(client_db_path)

    # SimulationTime.Y15S_FORMAT='%Y-%m-%dT%H%M%S'
    def test_get_simulation_dir_path(self):
        simulation_time = self.simulation_time
        simulation_dir_path = get_simulation_dir_path(simulation_time)
        self.assertFalse(os.path.isdir(simulation_dir_path))
        self.assert_simulation_dir_path(simulation_dir_path)

    def test_get_simulation_schema_path(self):
        simulation_time = self.simulation_time
        simulation_schema_path = get_simulation_schema_path(simulation_time)
        self.assertFalse(os.path.isfile(simulation_schema_path))
        self.assertNotRegex(simulation_schema_path,
                            ATAT_SIMULATION_TIME)
        self.assertRegex(simulation_schema_path, RE_Y15S)

    def test_get_root_path(self):
        self.assertEqual(get_root_path(), UMATOBI_ROOT_PATH)
        self.assertEqual(re.sub(TESTS_PATH, '', UMATOBI_ROOT_PATH), os.sep + 'umatobi-root')
        self.assertRegex(get_root_path(), UMATOBI_ROOT_PATH)

    def test_set_simulation_schema(self):
        simulation_time = SimulationTime()
        simulation_dir_path = get_simulation_dir_path(simulation_time)
        simulation_schema_path = get_simulation_schema_path(simulation_time)

        self.assertFalse(os.path.isfile(simulation_schema_path))
        with self.assertLogs('umatobi', level='INFO') as cm:
            simulation_schema_path = set_simulation_schema(simulation_time)
        self.assertTrue(os.path.isfile(simulation_schema_path))

        self.assertEqual(cm.output[0],
                f"INFO:umatobi:os.makedirs('{simulation_dir_path}')")
        self.assertRegex(cm.output[0],
                fr"^INFO:umatobi:os.makedirs\('/.+/{RE_Y15S}'\)$")
        self.assertEqual(cm.output[1],
                f"INFO:umatobi:shutil.copyfile(SIMULATION_SCHEMA_ORIG={SIMULATION_SCHEMA_ORIG}, simulation_schema_path={simulation_schema_path})")
        self.assertRegex(cm.output[1],
                fr"^INFO:umatobi:shutil.copyfile\(SIMULATION_SCHEMA_ORIG=.+, simulation_schema_path=.+\)$")

    @patch('os.path.isfile', return_value=True)
    def test_set_simulation_schema_pass(self, mock_isfile):
        simulation_time = SimulationTime()
        simulation_dir_path = get_simulation_dir_path(simulation_time)
        simulation_schema_path = get_simulation_schema_path(simulation_time)

        try:
            with self.assertLogs('umatobi', level='INFO') as cm:
                simulation_schema_path = set_simulation_schema(simulation_time)
        except AssertionError as err:
            self.assertEqual(err.args[0], 'no logs of level INFO or higher triggered on umatobi')

        mock_isfile.assert_called_once_with(simulation_schema_path)

    def test_get_master_palm_path(self):
        simulation_time = self.simulation_time
        self.assertEqual(
            get_master_palm_path(simulation_time),
            os.path.join(SIMULATION_ROOT_PATH,
                         simulation_time.get_y15s(),
                         MASTER_PALM))

    @patch('os.path.isdir', return_value=False)
    @patch('os.makedirs')
    def test_make_simulation_dir(self, mock_makedirs, mock_isdir):
        simulation_time = SimulationTime()
        simulation_dir_path = get_simulation_dir_path(simulation_time)

        mock_isdir.assert_not_called()
        with self.assertLogs('umatobi', level='INFO') as cm:
            make_simulation_dir(simulation_dir_path)
        self.assertRegex(cm.output[0], fr"^INFO:umatobi:os.makedirs\('/.+/{RE_Y15S}'\)$")
        self.assertEqual(cm.output[0], f"INFO:umatobi:os.makedirs('{simulation_dir_path}')")
        mock_isdir.assert_called_once()
        mock_makedirs.assert_called_with(simulation_dir_path)

    @patch('os.path.isdir', return_value=True)
    @patch('os.makedirs')
    def test_make_simulation_dir_pass(self, mock_makedirs, mock_isdir):
        simulation_time = SimulationTime()
        simulation_dir_path = get_simulation_dir_path(simulation_time)

        mock_isdir.assert_not_called()

        make_simulation_dir(simulation_dir_path)

        mock_isdir.assert_called_once()
        mock_makedirs.assert_not_called()

    def test_validate_kwargs(self):
        pass

    def test_dict2bytes(self):
        d = {
            'port': 1000,
            'host': 'localhost',
            'key': '0x' + '1234567890abcedf' * 4,
        }

        self.assertIsInstance(d, dict)
        b = dict2bytes(d)
        self.assertIsInstance(b, bytes)
        self.assertEqual(b, b'{"port": 1000, "host": "localhost", "key": "0x1234567890abcedf1234567890abcedf1234567890abcedf1234567890abcedf"}\n')

    def test_bytes2dict(self):
        d = {
            'port': 1000,
            'host': 'localhost',
            'key': '0x' + '1234567890abcedf' * 4,
        }
        expected_d = d

        b = dict2bytes(d)
        d2 = bytes2dict(b)
        self.assertIsInstance(d2, dict)
        self.assertNotEqual(id(d2), id(d))
        self.assertEqual(d2, expected_d)

    def test_dict2json(self):
        d = {
            'port': 1000,
            'host': 'localhost',
            'key': '0x' + '1234567890abcedf' * 4,
        }

        self.assertIsInstance(d, dict)
        j = dict2json(d)
        self.assertIsInstance(j, str)
        self.assertEqual(j, '{"port": 1000, "host": "localhost", "key": "0x1234567890abcedf1234567890abcedf1234567890abcedf1234567890abcedf"}\n')

    def test_json2dict(self):
        d = {
            'port': 1000,
            'host': 'localhost',
            'key': '0x' + '1234567890abcedf' * 4,
        }
        expected_d = d

        j = dict2json(d)
        d2 = json2dict(j)
        self.assertIsInstance(d2, dict)
        self.assertNotEqual(id(d2), id(d))
        self.assertEqual(d2, expected_d)

    def test_tell_shutdown_time(self):
        pass

    def test_load_yaml(self):
        y = load_yaml(replace_atat_n('1'))
        expected_obj = {'a': 1}
        self.assertEqual(y, expected_obj)

    def test_load_yaml2(self):
        y = load_yaml(replace_atat_n('2'))
        expected_obj = {'b': {'c': 3, 'd': 4}}
        self.assertEqual(y, expected_obj)

    def test_load_yaml3(self):
        y = load_yaml(replace_atat_n('3'))
        expected_obj = {
            'e': {
                'id': 1,
                'now': datetime(2011, 11, 11, 11, 11, 44, 901234),
                'val_blob': b'binary',
                'val_integer': 100,
                'val_null': None,
                'val_real': 1.1,
                'val_text': 'text context'
            }
        }

        self.assertEqual(y, expected_obj)

    def test_load_yaml4(self):
        y = load_yaml(replace_atat_n('4'))
        expected_obj = {
            'foo': [
                'schema_path',
                 'table_name', {
                    'id': 1,
                    'val_blob': b'binary strings',
                    'val_num': 8,
                    'val_null': None
                }
            ]
        }

        self.assertEqual(y, expected_obj)

    def test_dump_yaml(self):
        d = {
            'id': 1,
            'val_null':    None,
            'val_integer': 100,
            'val_real':    1.1,
            'val_text':    'text context',
            'val_blob':    b'binary strings',
            'val_11':      b'\x11' * 32,
            'val_aa':      b'\xaa' * 32,
            'val_cc':      b'\xcc' * 32,
            'now':         datetime(2011, 11, 11, 11, 11, 44, 901234),
        }

        dumped_yaml = yaml.dump(d)
        expected_dump = '''id: 1
now: 2011-11-11 11:11:44.901234
val_11: !!binary |
  ERERERERERERERERERERERERERERERERERERERERERE=
val_aa: !!binary |
  qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqo=
val_blob: !!binary |
  YmluYXJ5IHN0cmluZ3M=
val_cc: !!binary |
  zMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMw=
val_integer: 100
val_null: null
val_real: 1.1
val_text: text context
'''
        self.assertEqual(dumped_yaml, expected_dump)

    def test_allot_numbers(self):
        total = 100
        an_allotment = 7
        # 14 = 100 // 7
        #  2 = 100  % 7
        heads, assigned_num, last = allot_numbers(total, an_allotment)
        self.assertEqual(heads, 15)
        self.assertEqual(assigned_num, 7)
        self.assertEqual(last, 2)

        total = 100
        an_allotment = 10
        heads, assigned_num, last = allot_numbers(total, an_allotment)
        self.assertEqual(heads, 10)
        self.assertEqual(assigned_num, 10)
        self.assertEqual(last, 10)

        total = 99
        an_allotment = 100
        heads, assigned_num, last = allot_numbers(total, an_allotment)
        self.assertEqual(heads, 1)
        self.assertEqual(assigned_num, total)
        self.assertEqual(last, total)

        total = 100
        an_allotment = 100
        heads, assigned_num, last = allot_numbers(total, an_allotment)
        self.assertEqual(heads, 1)
        self.assertEqual(assigned_num, total)
        self.assertEqual(last, total)

        total = 101
        an_allotment = 100
        heads, assigned_num, last = allot_numbers(total, an_allotment)
        self.assertEqual(heads, 2)
        self.assertEqual(assigned_num, an_allotment)
        self.assertEqual(last, 1)

    # DONE, at least

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

    def test_sock_connect_fail1(self):
        host, port, v4_v6, tcp_udp = None, 44444, 'v4', 'tcp'
        addr = host, port
        with patch('umatobi.lib.socket.socket') as mock_socket:
            self.assertIsNone(sock_connect(None, host, port, v4_v6, tcp_udp))
        mock_socket.assert_not_called()

    def test_sock_connect_fail2(self):
        host, port, v4_v6, tcp_udp = 'localhost', None, 'v4', 'tcp'
        addr = host, port
        with patch('umatobi.lib.socket.socket') as mock_socket:
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

    # logger.py

    def test_make_log_dir(self):
        special_dir = os.path.dirname(get_master_palm_path(self.simulation_time))
        self.assertFalse(os.path.isdir(special_dir))
        tlogger = make_logger(log_dir=special_dir, name='special', id_=None, level="INFO")
        self.assertTrue(os.path.isdir(special_dir))
        shutil.rmtree(special_dir)

        self.assertFalse(os.path.isdir(special_dir))
        tlogger = make_logger(log_dir=special_dir, name='special', id_=10, level="INFO")
        self.assertTrue(os.path.isdir(special_dir))
        shutil.rmtree(special_dir)

        special_dir = os.path.dirname(get_master_palm_path(self.simulation_time))
        self.assertFalse(os.path.isdir(special_dir))
        tlogger = make_logger(log_dir=special_dir, name='', id_=None, level="INFO")
        self.assertTrue(os.path.isdir(special_dir))
        shutil.rmtree(special_dir)

        self.assertFalse(os.path.isdir(special_dir))
        tlogger = make_logger(log_dir=special_dir, name='', id_=10, level="INFO")
        self.assertTrue(os.path.isdir(special_dir))
        shutil.rmtree(special_dir)

    def test_log_path(self):
        special_dir = os.path.dirname(get_master_palm_path(self.simulation_time))
        tlogger = make_logger(log_dir=special_dir, name='test_logger', id_=None, level="INFO")
        self.assertEqual(tlogger.log_path, os.path.join(special_dir, 'test_logger.log', ))

        special_dir = os.path.dirname(get_master_palm_path(self.simulation_time))
        tlogger = make_logger(log_dir=special_dir, name='test_logger', id_=888, level="INFO")
        self.assertEqual(tlogger.log_path, os.path.join(special_dir, 'test_logger.888.log', ))

    # fail test

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

class PollingTests(unittest.TestCase):

    def test_sleep(self):
        pass

    def test___init__(self):
        pass

    def test_polling(self):
        pass

    def test_is_continue(self):
        pass

    def test__polling(self):
        pass

    def test_run(self):
        pass

class SimulationTimeTests(unittest.TestCase):

    def setUp(self):
        self.simulation_dir_path = \
            os.path.join(SIMULATION_ROOT_PATH, SIMULATION_DIR_PATH)
        self.simulation_time = SimulationTime()

    def tearDown(self):
        shutil.rmtree(os.path.dirname(get_master_palm_path(self.simulation_time)), ignore_errors=True)

    def test_time_machine_now(self):
        start_up_orig = SimulationTime.now()

        with time_machine(start_up_orig):
            simulation_time = SimulationTime()
        self.assertIsInstance(simulation_time.start_up_orig,
                              datetime)
        self.assertEqual(simulation_time.start_up_orig, start_up_orig)

    def test_mock_datetime_now(self):
        manipulated_datetime = datetime(2011, 11, 11, 11, 11, 11, 111111)
        with time_machine(manipulated_datetime):
            self.assertEqual(SimulationTime.now(), manipulated_datetime)

    def test_iso8601_to_time(self):
        isoformat = '2011-11-11T11:11:11.111111'
        self.assertEqual(SimulationTime.iso8601_to_time(isoformat), SimulationTime(datetime(2011, 11, 11, 11, 11, 11, 111111)))

    def test_time_to_iso8601(self):
        start_up_orig = datetime(2011, 11, 11, 11, 11, 11, 111111)
        with time_machine(start_up_orig):
            self.assertEqual(SimulationTime.time_to_iso8601(SimulationTime()), '2011-11-11T11:11:11.111111')

    def test_y15s_to_time(self):
        pass

    def test_time_to_y15s(self):
        # Y15S_FORMAT='%Y-%m-%dT%H%M%S'
        simulation_time = self.simulation_time
        y15s = SimulationTime.time_to_y15s(simulation_time)
        self.assertIsInstance(y15s, str)
        self.assertRegex(y15s, r"\A\d{4}-\d{2}-\d{2}T\d{6}\Z")

    def test_time_to_y15s_2(self):
        # Y15S_FORMAT='%Y-%m-%dT%H%M%S'
        y15s = SimulationTime.time_to_y15s(SimulationTime())
        self.assertIsInstance(y15s, str)
        self.assertRegex(y15s, r"\A\d{4}-\d{2}-\d{2}T\d{6}\Z")

    def test___init__(self):
        self.assertIsInstance(self.simulation_time.start_up_orig, datetime)

    def test___str__(self):
        pass

    def test___repr__(self):
        pass

    def test___eq__(self):
        pass

    def test_get_iso8601(self):
        self.assertRegex(self.simulation_time.get_iso8601(), RE_ISO8601)

    def test_get_y15s(self):
        self.assertRegex(self.simulation_time.get_y15s(), RE_Y15S)

    def test_passed_seconds(self):
        simulation_time = SimulationTime()
        passed_seconds = 123.456
        passed_time = timedelta(seconds=passed_seconds)

        with time_machine(simulation_time.start_up_orig + passed_time):
            self.assertEqual(simulation_time.passed_seconds(),
                             passed_seconds)

    def test_passed_ms(self):
        mili555 = timedelta(milliseconds=555)
        simulation_time = SimulationTime()
        start_up_orig = simulation_time.start_up_orig
        with time_machine(start_up_orig + mili555):
            passed_ms = simulation_time.passed_ms(SimulationTime().start_up_orig)
        self.assertEqual(passed_ms, 555)

    def test_make_start_up_orig_with_time_machine(self):
        start_up_orig = self.simulation_time.start_up_orig

        years_1000 = timedelta(days=1000*365)
        past = start_up_orig - years_1000
        current = start_up_orig
        future = start_up_orig + years_1000

        with time_machine(past):
            self.assertEqual(SimulationTime().start_up_orig, past)

        with time_machine(current):
            self.assertEqual(SimulationTime().start_up_orig, current)

        with time_machine(future):
            self.assertEqual(SimulationTime().start_up_orig, future)

class SchemaParserTests(unittest.TestCase):

    def assert_simulation_schema_path(self, inspected_path):
        self.assert_simulation_dir_path(inspected_path)
        self.assertRegex(inspected_path, f"{SIMULATION_SCHEMA}$")

    def assert_simulation_dir_path(self, dir_path):
        self.assertNotRegex(dir_path, ATAT_SIMULATION_TIME)
        self.assertRegex(dir_path, RE_Y15S)

    def setUp(self):
        self.simulation_dir_path = \
            os.path.join(SIMULATION_ROOT_PATH, SIMULATION_DIR_PATH)
        self.simulation_time = SimulationTime()

    def tearDown(self):
        shutil.rmtree(os.path.dirname(get_master_palm_path(self.simulation_time)), ignore_errors=True)

    def test___init__(self):
        simulation_time = self.simulation_time
        simulation_schema_path = set_simulation_schema(simulation_time)
        self.assert_simulation_schema_path(simulation_schema_path)

        schema_parser = SchemaParser(simulation_schema_path)
        self.assertEqual(schema_parser.schema_path, simulation_schema_path)

        self.assertEqual(schema_parser.schema_path, simulation_schema_path)
        self.assertEqual(schema_parser.table_names(), ['simulation', 'clients', 'growings', 'nodes'])
        self.assertIsInstance(schema_parser.converter_tables, dict)
        # see test_construct_converter_tables()
        # if you hope to make sense about converter_tables structure

    def test_data_type_converter(self):
        d_schema = {
            'column_blob': 'blob',
            'column_real': 'real',
            'column_integer': 'integer',
            'column_text': 'text',
        }

        d_values = {
#           'column_blob': 'blob',
            'column_blob': 'YmxvYg==',
            'column_real': '-1.0',
            'column_integer': '10',
            'column_text': 'text',
        }
        expected_values = {
            'column_blob': b'blob',
            'column_real': -1.0,
            'column_integer': 10,
            'column_text': 'text',
        }
        for column_name, data_type in d_schema.items():
            converter_name = d_schema[column_name]
            converter = SchemaParser.DATA_TYPE_CONVERTER[converter_name]
          # print('column_name =', column_name)
          # print('data_type =', data_type)
            self.assertEqual(converter(d_values[column_name]),
                             expected_values[column_name])

    def test_construct_converter_tables(self):
        # tests/assets/test.schema
        expected_tables = {
            'test_table': {
                'id': converter_integer,

                # None in Python
                'val_null': converter_null,

                # int in Python
                'val_integer': converter_integer,

                # float in Python
                'val_real':    converter_real,

                # depends on text_factory, str by default in Python
                'val_text':    converter_text,

                # bytes in Python
                'val_blob':    converter_blob,

                # time.time() in Python time format '2012-11-02T23:22:27.002'
                'now':    converter_text,

                # float
                'elapsed_time':    converter_real,

                # text
                'iso8601':    converter_text,
            }
        }

        schema_parser = SchemaParser(TESTS_SCHEMA_PATH)
        self.assertEqual(schema_parser.schema_path, TESTS_SCHEMA_PATH)

        self.assertEqual(schema_parser.converter_tables['test_table'],
                         expected_tables['test_table'])

    def test_get_table_names(self):
        expected_items = {
            'simulation': (
                'title', 'start_up_iso8601', 'open_office_iso8601',
                'close_office_iso8601', 'end_up_iso8601', 'simulation_seconds',
                'watson_office_addr', 'total_nodes', 'n_clients', 'memo',
                'log_level', 'version',
            ),
            'clients': (
                'id', 'addr', 'consult_iso8601', 'thanks_iso8601',
                'num_nodes', 'node_index', 'log_level'
            ),
            'growings': (
                'id', 'now_iso8601', 'pickle'
            ),
            'nodes': (
                'id', 'now_iso8601', 'addr', 'key', 'status'
            ),
        }

        simulation_time = self.simulation_time
        simulation_schema_path = set_simulation_schema(simulation_time)
        self.assert_simulation_schema_path(simulation_schema_path)

        schema_parser = SchemaParser(simulation_schema_path)
        self.assertEqual(schema_parser.schema_path, simulation_schema_path)
        self.assertSequenceEqual(schema_parser.get_table_names(),
                           tuple(expected_items.keys()))

    def test_get_table_names_from_schema(self):
        simulation_time = self.simulation_time
        simulation_schema_path = set_simulation_schema(simulation_time)
        self.assert_simulation_schema_path(simulation_schema_path)

        schema_parser = SchemaParser(simulation_schema_path)
        self.assertEqual(schema_parser.schema_path, simulation_schema_path)

        expected_table_names = ('simulation', 'clients', 'growings', 'nodes')
        self.assertSequenceEqual(schema_parser.get_table_names(),
                                 expected_table_names)

    def test_get_columns(self):
        expected_items = {
            'simulation': (
                'title', 'start_up_iso8601', 'open_office_iso8601',
                'close_office_iso8601', 'end_up_iso8601', 'simulation_seconds',
                'watson_office_addr', 'total_nodes', 'n_clients', 'memo',
                'log_level', 'version',
            ),
            'clients': (
                'id', 'addr', 'consult_iso8601', 'thanks_iso8601',
                'num_nodes', 'node_index', 'log_level'
            ),
            'growings': (
                'id', 'now_iso8601', 'pickle'
            ),
            'nodes': (
                'id', 'now_iso8601', 'addr', 'key', 'status'
            ),
        }

        simulation_time = self.simulation_time
        simulation_schema_path = set_simulation_schema(simulation_time)
        self.assert_simulation_schema_path(simulation_schema_path)

        schema_parser = SchemaParser(simulation_schema_path)
        self.assertEqual(schema_parser.schema_path, simulation_schema_path)
        for table_name in schema_parser.table_names():
            self.assertSequenceEqual(tuple(schema_parser.get_columns(table_name).keys()),
                                           expected_items[table_name])

    def test_parse_record(self):
        pass

    def test_spawn_records(self):
        simulation_conf_str = f'''
[simulation]
title: in test_schema_parser()
start_up_iso8601: 2011-11-11T11:11:11.123456
open_office_iso8601: 2011-11-11T11:11:12.789012
close_office_iso8601: 2011-11-11T11:11:42.345678
end_up_iso8601: 2011-11-11T11:11:44.901234
simulation_seconds: 30
watson_office_addr: localhost:11111
total_nodes: 1000
n_clients: 4
memo: test to combine schema_parser and simulation.conf
log_level: INFO
version: 0.0.0

[nodes]
id: 100
now_iso8601: 2011-12-22T11:11:44.901234
addr: 127.0.0.1:22222
key: qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqo=
status: active
'''
# >>> base64.b64encode(b'\xaa\xaa\xaa')
# b'qqqq'
# >>> base64.b64decode(b'qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqo=')
# b'\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa'

        simulation_time = self.simulation_time
        simulation_schema_path = set_simulation_schema(simulation_time)
        self.assert_simulation_schema_path(simulation_schema_path)

        schema_parser = SchemaParser(simulation_schema_path)
        self.assertEqual(schema_parser.schema_path, simulation_schema_path)
        config = configparser.ConfigParser()
        config.read_string(simulation_conf_str)
      # print('config.sections =', tuple(config.sections()))

        records = schema_parser.spawn_records(config,
                                              table_names=config.sections())
        self.assertEqual(records.simulation['title'], 'in test_schema_parser()')
        self.assertEqual(records.simulation['start_up_iso8601'], '2011-11-11T11:11:11.123456')
        self.assertEqual(records.simulation['open_office_iso8601'], '2011-11-11T11:11:12.789012')
        self.assertEqual(records.simulation['close_office_iso8601'], '2011-11-11T11:11:42.345678')
        self.assertEqual(records.simulation['end_up_iso8601'], '2011-11-11T11:11:44.901234')
        self.assertEqual(records.simulation['simulation_seconds'], 30)
        self.assertEqual(records.simulation['watson_office_addr'], 'localhost:11111')
        self.assertEqual(records.simulation['total_nodes'], 1000)
        self.assertEqual(records.simulation['n_clients'], 4)
        self.assertEqual(records.simulation['memo'], 'test to combine schema_parser and simulation.conf')
        self.assertEqual(records.simulation['log_level'], 'INFO')
        self.assertEqual(records.simulation['version'], '0.0.0')

        self.assertEqual(records.nodes['id'], 100)
        self.assertEqual(records.nodes['now_iso8601'], '2011-12-22T11:11:44.901234')
        self.assertEqual(records.nodes['addr'], '127.0.0.1:22222')
        self.assertEqual(records.nodes['key'], b'\xaa' * Key.KEY_OCTETS)
        self.assertEqual(records.nodes['status'], 'active')

    def test_set_converter(self):
        sp = schema_parser = SchemaParser(TESTS_SCHEMA_PATH)
        self.assertEqual(schema_parser.schema_path, TESTS_SCHEMA_PATH)

        with self.assertRaises(KeyError):
            schema_parser.converter_tables['test_table']['blob_column']
        schema_parser.set_converter('test_table', 'blob_column', 'blob')
        self.assertEqual(schema_parser.converter_tables['test_table']['blob_column'], converter_blob)

        with self.assertRaises(KeyError):
            schema_parser.converter_tables['test_table']['real_column']
        schema_parser.set_converter('test_table', 'real_column', 'real')
        self.assertEqual(schema_parser.converter_tables['test_table']['real_column'], converter_real)

        with self.assertRaises(KeyError):
            schema_parser.converter_tables['test_table']['integer_column']
        schema_parser.set_converter('test_table', 'integer_column', 'integer')
        self.assertEqual(schema_parser.converter_tables['test_table']['integer_column'], converter_integer)

        with self.assertRaises(KeyError):
            schema_parser.converter_tables['test_table']['text_column']
        schema_parser.set_converter('test_table', 'text_column', 'text')
        self.assertEqual(schema_parser.converter_tables['test_table']['text_column'], converter_text)

        with self.assertRaises(KeyError):
            schema_parser.converter_tables['test_table']['null_column']
        schema_parser.set_converter('test_table', 'null_column', 'null')
        self.assertEqual(schema_parser.converter_tables['test_table']['null_column'], converter_null)

    def test_get_converter(self):
        sp = schema_parser = SchemaParser(TESTS_SCHEMA_PATH)
        self.assertEqual(schema_parser.schema_path, TESTS_SCHEMA_PATH)
        self.assertEqual(sp.get_converter('test_table', 'id'),
                         converter_integer)
        self.assertEqual(sp.get_converter('test_table', 'val_null'),
                         converter_null)
        self.assertEqual(sp.get_converter('test_table', 'val_integer'),
                         converter_integer)
        self.assertEqual(sp.get_converter('test_table', 'val_real'),
                         converter_real)
        self.assertEqual(sp.get_converter('test_table', 'val_text'),
                         converter_text)
        self.assertEqual(sp.get_converter('test_table', 'val_blob'),
                         converter_blob)

if __name__ == '__main__':
    unittest.main()
