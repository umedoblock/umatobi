import os, sys, datetime, shutil
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

from umatobi.tests import *
from umatobi.log import logger, make_logger
from umatobi import lib
from umatobi.lib import *

class LibTests(unittest.TestCase):

    def setUp(self):
        self.tests_simulation_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'umatobi-simulation').replace('/unit/', '/')

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

    def test_sock_send_ok_tcp(self):
        with patch('umatobi.lib.socket', spec_set=True, new_callable=MagicMock):
            tcp_sock = sock_create('v4', 'tcp')

        send_data = b'send mocked data'
        result = sock_send(tcp_sock, send_data)
        tcp_sock.sendall.assert_called_once_with(send_data)
        self.assertTrue(result)

        with patch('umatobi.lib.socket', spec_set=True, new_callable=MagicMock) as mock_sock:
            tcp_sock = sock_create('v4', 'tcp')
        mock_sock.socket.assert_called_once_with(mock_sock.AF_INET, mock_sock.SOCK_STREAM)

        with patch.object(tcp_sock, 'sendall', side_effect=socket.timeout):
            with self.assertLogs('umatobi', level='INFO') as cm:
                result = sock_send(tcp_sock, send_data)
        self.assertRegex(cm.output[0], r".+ got timeout\.")
        self.assertFalse(result)

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

        with patch.object(udp_sock, 'recv', side_effect=socket.timeout):
            recved_data = sock_recv(udp_sock, 1024)
        self.assertIsNone(recved_data)

    def test_get_host_port(self):
        host_port = 'localhost:8888'
        self.assertEqual(get_host_port(host_port), ('localhost', 8888))
        host_port = '192.168.1.1:9999'
        self.assertEqual(get_host_port(host_port), ('192.168.1.1', 9999))

    def test_data_type_converter(self):
        d_schema = {
            'column_blob': 'blob',
            'column_float': 'float',
            'column_integer': 'integer',
            'column_text': 'text',
        }

        d_values = {
            'column_blob': 'blob',
            'column_float': '-1.0',
            'column_integer': '10',
            'column_text': 'text',
        }
        expected_values = {
            'column_blob': b'blob',
            'column_float': -1.0,
            'column_integer': 10,
            'column_text': 'text',
        }
        for column_name, data_type in d_schema.items():
            converter_name = d_schema[column_name]
            converter = DATA_TYPE_CONVERTER[converter_name]
            self.assertEqual(converter(d_values[column_name]),
                             expected_values[column_name])

    def test_get_db_from_schema(self):
        # SCHEMA_PATH='umatobi/simulator/simulation.schema'
        config_db = ConfigDb(SCHEMA_PATH)

        expected_table_names = ('simulation', 'nodes', 'clients', 'growings')
        self.assertSequenceEqual(config_db.table_names(), expected_table_names)
       #print('config_db.table_names() =', config_db.table_names())
       #for table_name in config_db.table_names():
       #    print('table_name =', table_name)
       #    print(f'config_db[{table_name}] = {config_db[table_name]}')
       #    print(f'config_db[{table_name}].items() = {config_db[table_name].items()}')
       #    for column, data_type in config_db[table_name].items():
       #        print(f'column={column}, data_type={data_type}')

    def test_get_table_columns(self):
        expected_items = {
            'simulation': (
                'watson_office_addr', 'simulation_ms', 'title',
                'memo', 'version', 'n_clients', 'total_nodes'
            ),
            'nodes': (
                'id', 'office_addr', 'keyid', 'key', 'rad', 'x', 'y', 'status'
            ),
            'clients': (
                'id', 'host', 'port', 'joined', 'log_level',
                'num_nodes', 'node_index'
            ),
            'growings': ( 'id', 'elapsed_time', 'pickle')

        }

        config_db = ConfigDb(SCHEMA_PATH)
        self.assertSequenceEqual(config_db.table_names(),
                           tuple(expected_items.keys()))

        for table_name in config_db.table_names():
           #for column, data_type in config_db[table_name].items():
               #print(table_name, column, data_type)
               #print(tuple(config_db[table_name].keys()))
               #print(expected_items[table_name])
            self.assertSequenceEqual(tuple(config_db[table_name].keys()),
                                           expected_items[table_name])

    def test_dict2json_and_json2dict(self):
        d = {
            'port': 1000,
            'host': 'localhost',
            'key': '0x' + '1234567890abcedf' * 4,
        }

        self.assertIsInstance(d, dict)
        j = lib.dict2json(d)
        self.assertIsInstance(j, str)
        d2 = lib.json2dict(j)
        self.assertIsInstance(d2, dict)
        self.assertNotEqual(id(d2), id(d))
        self.assertEqual(d2, d)

    def test_dict2bytes_and_bytes2dict(self):
        d = {
            'port': 1000,
            'host': 'localhost',
            'key': '0x' + '1234567890abcedf' * 4,
        }

        self.assertIsInstance(d, dict)
        b = lib.dict2bytes(d)
        self.assertIsInstance(b, bytes)
        d2 = lib.bytes2dict(b)
        self.assertIsInstance(d2, dict)
        self.assertNotEqual(id(d2), id(d))
        self.assertEqual(d2, d)

    def test_SIMULATION_DIR(self):
        self.assertEqual(SIMULATION_DIR, self.tests_simulation_dir)

    def test_master_hand(self):
        start_up_orig = lib.make_start_up_orig()
        start_up_time = lib.make_start_up_time(start_up_orig)
        self.assertEqual(lib.get_master_hand(start_up_orig), f"{start_up_time}/{MASTER_HAND}")

    def test_master_hand_path(self):
        start_up_orig = lib.make_start_up_orig()
        start_up_time = lib.make_start_up_time(start_up_orig)
        self.assertEqual(lib.get_master_hand_path(SIMULATION_DIR, start_up_orig), os.path.join(self.tests_simulation_dir, f"{start_up_time}/{MASTER_HAND}"))

    def test_make_log_dir(self):
        special_dir = SIMULATION_DIR + "-special"
        self.assertFalse(os.path.isdir(special_dir))
        tlogger = make_logger(log_dir=special_dir, name='special', id_=None, level="INFO")
        self.assertTrue(os.path.isdir(special_dir))
        shutil.rmtree(special_dir)

        self.assertFalse(os.path.isdir(special_dir))
        tlogger = make_logger(log_dir=special_dir, name='special', id_=10, level="INFO")
        self.assertTrue(os.path.isdir(special_dir))
        shutil.rmtree(special_dir)

        special_dir = SIMULATION_DIR + "-special2"
        self.assertFalse(os.path.isdir(special_dir))
        tlogger = make_logger(log_dir=special_dir, name='', id_=None, level="INFO")
        self.assertTrue(os.path.isdir(special_dir))
        shutil.rmtree(special_dir)

        self.assertFalse(os.path.isdir(special_dir))
        tlogger = make_logger(log_dir=special_dir, name='', id_=10, level="INFO")
        self.assertTrue(os.path.isdir(special_dir))
        shutil.rmtree(special_dir)

    def test_log_path(self):
        tlogger = make_logger(log_dir=SIMULATION_DIR, name='test_logger', id_=None, level="INFO")
        self.assertEqual(tlogger.log_path, os.path.join(self.tests_simulation_dir, 'test_logger.log', ))

        tlogger = make_logger(log_dir=SIMULATION_DIR, name='test_logger', id_=888, level="INFO")
        self.assertEqual(tlogger.log_path, os.path.join(self.tests_simulation_dir, 'test_logger.888.log', ))

    def test_make_start_up_orig(self):
        start_up_orig = lib.make_start_up_orig()
        self.assertIsInstance(start_up_orig, datetime.datetime)

    def test_make_start_up_orig_with_time_machine(self):
        start_up_orig = lib.make_start_up_orig()
        years_1000 = datetime.timedelta(days=1000*365)

        past = start_up_orig - years_1000
        current = start_up_orig
        future = start_up_orig + years_1000

        with time_machine(past):
            self.assertEqual(lib.make_start_up_orig(), past)

        with time_machine(current):
            self.assertEqual(lib.make_start_up_orig(), current)

        with time_machine(future):
            self.assertEqual(lib.make_start_up_orig(), future)

    def test_curren_y15sformat_time(self):
        # Y15S_FORMAT='%Y-%m-%dT%H%M%S'
        y15s = lib.current_y15sformat_time()
        self.assertIsInstance(y15s, str)
        self.assertRegex(y15s, r"\A\d{4}-\d{2}-\d{2}T\d{6}\Z")

    def test_y15sformat_time(self):
        start_up_orig = lib.make_start_up_orig()
        # Y15S_FORMAT='%Y-%m-%dT%H%M%S'
        y15s = lib.y15sformat_time(start_up_orig)
        self.assertIsInstance(y15s, str)
        self.assertRegex(y15s, r"\A\d{4}-\d{2}-\d{2}T\d{6}\Z")

    def test_elapsed_time(self):
        td = D_TIMEDELTA.get(self._testMethodName, TD_ZERO)

        start_up_orig = lib.make_start_up_orig()
        et = lib.elapsed_time(start_up_orig - td)
        self.assertEqual(73138, et)

    def mocked_datetime_now(mocked_datetime=None):
        if not mocked_datetime:
            return mocked_datetime
        else:
            return datetime.datetime.now()

    def test_from_isoformat_to_start_up_orig(self):
        isoformat = '2011-11-11T11:11:11.111111'
        self.assertEqual(lib.isoformat_to_start_up_orig(isoformat), datetime.datetime(2011, 11, 11, 11, 11, 11, 111111))

    def test_start_up_orig_to_isoformat(self):
        start_up_orig = datetime.datetime(2011, 11, 11, 11, 11, 11, 111111)
        self.assertEqual(lib.start_up_orig_to_isoformat(start_up_orig), '2011-11-11T11:11:11.111111')

    def test_mock_datetime_now(self):
        manipulated_datetime = datetime.datetime(2011, 11, 11, 11, 11, 11, 111111)
        with time_machine(manipulated_datetime):
            self.assertEqual(lib.datetime_now(), manipulated_datetime)

if __name__ == '__main__':
    unittest.main()
