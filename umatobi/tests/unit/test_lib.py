import os, sys, re, shutil
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
from datetime import datetime, timedelta

from umatobi.tests import *
from umatobi.log import make_logger
from umatobi.lib import *
from umatobi.simulator.core.key import Key

class LibTests(unittest.TestCase):

    RE_Y15S = r'20\d{2}-[01]\d{1}-[0123]\dT[012]\d[0-5]\d[0-5]\d'
    RE_ISO8601 = r'20\d{2}-[01]\d{1}-[0123]\dT[012]\d:[0-5]\d:[0-5]\d\.\d{6}'

    def assert_simulation_schema_path(self, inspected_path):
        self.assert_simulation_dir_path(inspected_path)
        self.assertRegex(inspected_path, f"{SIMULATION_SCHEMA}$")

    def assert_simulation_dir_path(self, dir_path):
        self.assertTrue(os.path.isdir(os.path.dirname(dir_path)))
        self.assertNotRegex(dir_path,
                            SIMULATION_TIME_ATAT)
        self.assertRegex(dir_path,
                         LibTests.RE_Y15S)

    def setUp(self):
        self.simulation_dir_path = \
            os.path.join(SIMULATION_ROOT_PATH, SIMULATION_DIR_PATH)
        self.simulation_time = SimulationTime()

    def tearDown(self):
        shutil.rmtree(os.path.dirname(get_master_palm_path(self.simulation_time)), ignore_errors=True)

    def test_simulation_time(self):
        start_up_orig = SimulationTime.now()

        with time_machine(start_up_orig):
            simulation_time = SimulationTime()
        self.assertIsInstance(simulation_time.start_up_orig,
                              datetime)
        self.assertEqual(simulation_time.start_up_orig, start_up_orig)

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

    def test_schema_parser(self):
        keyid = 'a' * Key.KEY_HEXES
        simulation_conf_str = f'''
[simulation]
watson_office_addr: localhost:11111
simulation_ms: 30000
title: in test_schema_parser()
memo: test to combine schema_parser and simulation.conf
version: 0.0.0
n_clients: 4
total_nodes: 1000

[nodes]
id: 100
office_addr: 127.0.0.1:22222
key: 0x{keyid}
status: active
'''

        simulation_time = self.simulation_time
        simulation_schema_path = get_simulation_schema_path(simulation_time)
        self.assert_simulation_schema_path(simulation_schema_path)

        schema_parser = SchemaParser(simulation_schema_path)
        config = configparser.ConfigParser()
        config.read_string(simulation_conf_str)
      # print('config.sections =', tuple(config.sections()))

        records = schema_parser.spawn_records(config,
                                              table_names=config.sections())
        self.assertEqual(records.simulation['watson_office_addr'], 'localhost:11111')
        self.assertEqual(records.simulation['simulation_ms'], 30000)
        self.assertEqual(records.simulation['title'], 'in test_schema_parser()')
        self.assertEqual(records.simulation['memo'], 'test to combine schema_parser and simulation.conf')
        self.assertEqual(records.simulation['version'], '0.0.0')
        self.assertEqual(records.simulation['n_clients'], 4)
        self.assertEqual(records.simulation['total_nodes'], 1000)

        self.assertEqual(records.nodes['id'], 100)
        self.assertEqual(records.nodes['office_addr'], '127.0.0.1:22222')
        self.assertEqual(records.nodes['key'], str.encode(f'0x{keyid}'))
        self.assertEqual(records.nodes['status'], 'active')

    def test_get_db_from_schema(self):
        simulation_time = self.simulation_time
        simulation_schema_path = get_simulation_schema_path(simulation_time)
        self.assert_simulation_schema_path(simulation_schema_path)

        schema_parser = SchemaParser(simulation_schema_path)

        expected_table_names = ('simulation', 'nodes', 'clients', 'growings')
        self.assertSequenceEqual(schema_parser.table_names(), expected_table_names)
       #print('schema_parser.table_names() =', schema_parser.table_names())
       #for table_name in schema_parser.table_names():
       #    print('table_name =', table_name)
       #    print(f'schema_parser[{table_name}] = {schema_parser[table_name]}')
       #    print(f'schema_parser[{table_name}].items() = {schema_parser[table_name].items()}')
       #    for column, data_type in schema_parser[table_name].items():
       #        print(f'column={column}, data_type={data_type}')

    # SimulationTime.Y15S_FORMAT='%Y-%m-%dT%H%M%S'
    def test_get_simulation_dir_path(self):
        simulation_time = self.simulation_time
        simulation_dir_path = get_simulation_dir_path(simulation_time)
        self.assertTrue(os.path.isdir(simulation_dir_path))
        self.assert_simulation_dir_path(simulation_dir_path)

    def test_get_simulation_schema_path(self):
        simulation_time = self.simulation_time
        simulation_schema_path = get_simulation_schema_path(simulation_time)
        self.assertTrue(os.path.isfile(simulation_schema_path))
        self.assertNotRegex(simulation_schema_path,
                            SIMULATION_TIME_ATAT)
        self.assertRegex(simulation_schema_path,
                         LibTests.RE_Y15S)

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

        simulation_time = self.simulation_time
        simulation_schema_path = get_simulation_schema_path(simulation_time)
        self.assert_simulation_schema_path(simulation_schema_path)
        schema_parser = SchemaParser(simulation_schema_path)
        self.assertSequenceEqual(schema_parser.table_names(),
                           tuple(expected_items.keys()))

        for table_name in schema_parser.table_names():
           #for column, data_type in schema_parser[table_name].items():
               #print(table_name, column, data_type)
               #print(tuple(schema_parser[table_name].keys()))
               #print(expected_items[table_name])
            self.assertSequenceEqual(tuple(schema_parser[table_name].keys()),
                                           expected_items[table_name])

    def test_dict2json_and_json2dict(self):
        d = {
            'port': 1000,
            'host': 'localhost',
            'key': '0x' + '1234567890abcedf' * 4,
        }

        self.assertIsInstance(d, dict)
        j = dict2json(d)
        self.assertIsInstance(j, str)
        d2 = json2dict(j)
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
        b = dict2bytes(d)
        self.assertIsInstance(b, bytes)
        d2 = bytes2dict(b)
        self.assertIsInstance(d2, dict)
        self.assertNotEqual(id(d2), id(d))
        self.assertEqual(d2, d)

    def test_some_PATHes(self):
        self.assertRegex(UMATOBI_ROOT_PATH, f"^{TESTS_PATH}")
        self.assertRegex(SIMULATION_ROOT_PATH, f"^{TESTS_PATH}")

        self.assertRegex(SIMULATION_DIR_PATH, r'/@@SIMULATION_TIME@@$')
        self.assertRegex(SIMULATION_SCHEMA_PATH, r'/tests/')

    def test_root_path(self):
        self.assertEqual(get_root_path(), UMATOBI_ROOT_PATH)
        self.assertEqual(re.sub(TESTS_PATH, '', UMATOBI_ROOT_PATH), os.sep + 'umatobi-root')
        self.assertRegex(get_root_path(), UMATOBI_ROOT_PATH)

    def test_get_iso8601(self):
        self.assertRegex(self.simulation_time.get_iso8601(), LibTests.RE_ISO8601)

    def test_get_y15s(self):
        self.assertRegex(self.simulation_time.get_y15s(), LibTests.RE_Y15S)

    def test_master_palm_path(self):
        simulation_time = self.simulation_time
        self.assertEqual(
            get_master_palm_path(simulation_time),
            os.path.join(SIMULATION_ROOT_PATH,
                         simulation_time.get_y15s(),
                         MASTER_PALM))

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

    def test_make_start_up_orig(self):
        simulation_time = self.simulation_time
        self.assertIsInstance(simulation_time.start_up_orig, datetime)

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

    def test_y15sformat_time(self):
        # Y15S_FORMAT='%Y-%m-%dT%H%M%S'
        simulation_time = self.simulation_time
        y15s = SimulationTime.time_to_y15s(simulation_time)
        self.assertIsInstance(y15s, str)
        self.assertRegex(y15s, r"\A\d{4}-\d{2}-\d{2}T\d{6}\Z")

    def test_curren_y15sformat_time(self):
        # Y15S_FORMAT='%Y-%m-%dT%H%M%S'
        y15s = SimulationTime.time_to_y15s(SimulationTime())
        self.assertIsInstance(y15s, str)
        self.assertRegex(y15s, r"\A\d{4}-\d{2}-\d{2}T\d{6}\Z")

    def test_simulation_time_passed_sec(self):
        pass

    # class timedelta(builtins.object)
    #  |  Difference between two datetime values.
    #  |
    #  |  timedelta(days=0, seconds=0, microseconds=0, milliseconds=0,
    #               minutes=0, hours=0, weeks=0)

    def test_simulation_time_passed_ms(self):
        mili555 = timedelta(milliseconds=555)
        simulation_time = SimulationTime()
        start_up_orig = simulation_time.start_up_orig
        with time_machine(start_up_orig + mili555):
            passed_ms = simulation_time.passed_ms(SimulationTime().start_up_orig)
        self.assertEqual(passed_ms, 555)

    def test_from_iso_to_start_up_orig(self):
        isoformat = '2011-11-11T11:11:11.111111'
        self.assertEqual(SimulationTime.iso8601_to_time(isoformat), SimulationTime(datetime(2011, 11, 11, 11, 11, 11, 111111)))

    def test_start_up_orig_to_iso(self):
        start_up_orig = datetime(2011, 11, 11, 11, 11, 11, 111111)
        with time_machine(start_up_orig):
            self.assertEqual(SimulationTime.time_to_iso8601(SimulationTime()), '2011-11-11T11:11:11.111111')

    def test_mock_datetime_now(self):
        manipulated_datetime = datetime(2011, 11, 11, 11, 11, 11, 111111)
        with time_machine(manipulated_datetime):
            self.assertEqual(SimulationTime.now(), manipulated_datetime)

if __name__ == '__main__':
    unittest.main()
