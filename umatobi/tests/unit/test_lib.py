# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import os, sys, re, shutil, pathlib, pickle
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
from datetime import datetime, timedelta

import yaml
from umatobi.tests import *
from umatobi.tests.constants import *
from umatobi.lib import *
from umatobi.simulator.core.key import Key
from umatobi.simulator.sql import SQL
from umatobi.simulator.node import Node

class LibTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.simulation_time = SimulationTime()
        cls.path_maker = PathMaker(cls.simulation_time)
        cls.path_maker.set_simulation_schema()

        # yaml_path = 'tests/assets/test.yaml'

        cls.test_db_path = TESTS_DB_PATH
        cls.test_yaml_path = replace_atat_n('')
        cls.test_schema_path = TESTS_SCHEMA_PATH
       #print('cls.test_db_path =', cls.test_db_path)
       #print('cls.test_yaml_path =', cls.test_yaml_path)
       #print('cls.test_schema_path =', cls.test_schema_path)
        if os.path.isfile(cls.test_db_path):
            os.remove(cls.test_db_path)
        cls.test_db = SQL(db_path=cls.test_db_path,
                          schema_path=cls.test_schema_path)
        cls.test_db.create_db()

        simulation_db_path = cls.path_maker.get_simulation_db_path()
        schema_path = cls.path_maker.get_simulation_schema_path()
        if os.path.isfile(simulation_db_path):
            os.remove(simulation_db_path)
        cls.simulation_db = SQL(db_path=simulation_db_path,
                                schema_path=schema_path)
        cls.simulation_db.create_db()

    @classmethod
    def tearDownClass(cls):

        cls.simulation_db.close()
        cls.simulation_db.remove_db()

        cls.test_db.close()
        cls.test_db.remove_db()

    def setUp(self):
        self.simulation_time = LibTests.simulation_time
        self.path_maker = LibTests.path_maker

    def tearDown(self):
        cleanup_file_paths = []
        cleanup_file_paths.append(self.path_maker.get_simulation_schema_path())
        cleanup_file_paths.append(self.path_maker.get_master_palm_txt_path())
        for cleanup_file_path in cleanup_file_paths:
            p = pathlib.Path(cleanup_file_path)
            if p.is_file():
                p.unlink()

    def test_make_fixture(self):
        expected_qwer = \
            ({
                'id': 4,
                'elapsed_time': 22222,
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

    def test_inserts_fixture_single(self):
        expected_schema_path, \
        expected_table_name, \
        expected_test_set_nodes = \
            '../../simulator/simulation.schema', \
            'clients', \
            ({
                'id': 0,
                'addr': 'localhost:10000',
                'consult_iso8601': '2011-12-22T11:11:44.901234',
                'thanks_iso8601': '2011-12-22T11:12:20.901234',
                'num_nodes': 10,
                'node_index': 0,
                'log_level': 'INFO',
             }, {
                'id': 1,
                'addr': 'localhost:10001',
                'consult_iso8601': '2011-12-22T11:11:44.901234',
                'thanks_iso8601': '2011-12-22T11:12:20.901234',
                'num_nodes': 10,
                'node_index': 10,
                'log_level': 'INFO',
            })

        db = LibTests.simulation_db
        schema_parser, table_name, fixture = \
            inserts_fixture(db, replace_atat_n(''), 'test_set_nodes')
      # select(self, table_name, select_columns='*', conditions=''):
       #print('rows =')
       #print(rows)

#       self.assertEqual(schema_parser.schema_path, get_simulation_schema_path(LibTests.start_up_orig))
        self.assertEqual(table_name, 'clients')
        self.assertEqual(fixture, expected_test_set_nodes)

        rows = db.select('clients')

       #print('rows =', rows)
       #print('rows[0] =', rows[0])
       #print('tuple(rows[0]) =', tuple(rows[0]))
        expected_tuple = [tuple(em.values()) for em in expected_test_set_nodes]
        self.assertEqual(len(rows), len(expected_test_set_nodes))
        inspect_tuple = [tuple(row) for row in rows]
       #print(' inspect_tuple =', inspect_tuple)
       #print('expected_tuple =', expected_tuple)
        self.assertEqual(inspect_tuple, expected_tuple)

    def test_inserts_fixture_multiple_times(self):
        expected_multiple = ( {
            'id': 0,
            'val_null':    None,
            'val_integer': 0,
            'val_real':    0.0,
            'val_text':    'multiple inserts 0',
            'val_blob':    b'multiple inserts 0',
            'now':          '2002-11-02T23:22:00.000',
            'elapsed_time': 100,
            'iso8601':      '2002-11-02T23:22:00.000000',
        }, {
            'id': 1,
            'val_null':    None,
            'val_integer': 1,
            'val_real':    1.1,
            'val_text':    'multiple inserts 1',
            'val_blob':    b'multiple inserts 1',
            'now':          '2112-11-12T23:22:11.111',
            'elapsed_time': 111,
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

    def test_some_PATHs(self):
        self.assertEqual(UMATOBI_MODULE_PATH, os.path.normpath(os.path.join(TESTS_PATH, '..')))
        self.assertEqual(SIMULATION_SCHEMA_PATH, os.path.join(UMATOBI_MODULE_PATH, SIMULATOR_DIR, SIMULATION_SCHEMA))
        self.assertRegex(SIMULATION_ROOT_PATH, r'/tests/umatobi-simulation$')
        self.assertRegex(UMATOBI_SIMULATION_DIR_PATH, r'/tests/umatobi-simulation/@@SIMULATION_TIME@@$')

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

    def test_make_growing_dict(self):
        from datetime import timedelta

        node_assets = make_node_assets()

        node = Node(host='localhost', id=1, **node_assets)
        key = b'\x01\x23\x45\x67\x89\xab\xcd\xef' * 4
        node.key.update(key)
        got_attrs = node.get_attrs()
        pickled_attrs = pickle.dumps(got_attrs)
        expected_growing_dict = {
            'id': 100,
            'elapsed_time': 111,
            'pickle': pickled_attrs,
        }

        simulation_time = SimulationTime()
        with time_machine(simulation_time.start_up_orig + \
                          timedelta(milliseconds=111)):
            elapsed_time = simulation_time.passed_ms()

        growing_dict = make_growing_dict(100, elapsed_time, pickled_attrs)

        self.assertEqual(growing_dict, expected_growing_dict)

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
            os.path.join(SIMULATION_ROOT_PATH, UMATOBI_SIMULATION_DIR_PATH)
        self.simulation_time = SimulationTime()
        self.path_maker = PathMaker(self.simulation_time)

    def tearDown(self):
        shutil.rmtree(self.path_maker.get_simulation_schema_path(), ignore_errors=True)

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

class PathMakerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.simulation_time = SimulationTime()
        cls.path_maker = PathMaker(cls.simulation_time)

    @classmethod
    def tearDownClass(cls):
        pass

    def assert_client_db_path(self, client_db_path):
        self.assertRegex(client_db_path, RE_CLIENT_N_DB)
        self.assertNotRegex(client_db_path, ATAT_N)

    def assert_simulation_schema_path(self, inspected_path):
        self.assert_simulation_dir_path(inspected_path)
        self.assertRegex(inspected_path, f'{SIMULATION_SCHEMA}$')

    def assert_simulation_dir_path(self, dir_path):
        self.assertTrue(os.path.isdir(os.path.dirname(dir_path)))
        self.assertNotRegex(dir_path,
                            ATAT_SIMULATION_TIME)
        self.assertRegex(dir_path, RE_Y15S)

    def setUp(self):
        self.path_maker = PathMakerTests.path_maker

#   def tearDown(self):
#       cleanup_paths = []
#       cleanup_paths.append(self.path_maker.get_simulation_schema_path())
#       cleanup_paths.append(self.path_maker.get_master_palm_txt_path())
#       for cleanup_path in cleanup_paths:
#           p = pathlib.Path(cleanup_path)
#           if p.is_file():
#               p.unlink()

    def test___eq__(self):
        iso8601 = SimulationTime().get_iso8601()
        simulation_time_0 = SimulationTime(iso8601)
        simulation_time_1 = SimulationTime(iso8601)
        path_maker_0 = PathMaker(simulation_time_0)
        path_maker_1 = PathMaker(simulation_time_1)

        self.assertEqual(path_maker_0, path_maker_1)
        self.assertEqual(simulation_time_0, simulation_time_1)
        self.assertNotEqual(id(path_maker_0.simulation_time),
                            id(path_maker_1.simulation_time))

    def test___init__(self):
        path_maker = self.path_maker
        self.assertIsInstance(path_maker, PathMaker)
        self.assertEqual(path_maker.simulation_time, \
                         PathMakerTests.simulation_time)

    def test_get_client_db_path(self):
        path_maker = self.path_maker
        client_id = 8
        client_db_path = path_maker.get_client_db_path(client_id)

        self.assertEqual(client_db_path,
                os.path.join(
                    re.sub(ATAT_SIMULATION_TIME,
                    path_maker.simulation_time.get_y15s(),
                    UMATOBI_SIMULATION_DIR_PATH), 'client.8.db'))

        client_id = 88888
        client_db_path = path_maker.get_client_db_path(client_id)
        self.assert_client_db_path(client_db_path)

    # SimulationTime.Y15S_FORMAT='%Y-%m-%dT%H%M%S'
    def test_get_simulation_dir_path(self):
        path_maker = self.path_maker
        simulation_dir_path = path_maker.get_simulation_dir_path()
        self.assert_simulation_dir_path(simulation_dir_path)

    def test_get_simulation_schema_path(self):
        path_maker = self.path_maker
        simulation_schema_path = path_maker.get_simulation_schema_path()
        self.assertFalse(os.path.isfile(simulation_schema_path))
        self.assertNotRegex(simulation_schema_path,
                            ATAT_SIMULATION_TIME)
        self.assertRegex(simulation_schema_path, RE_Y15S)

    def test_get_module_path(self):
        path_maker = self.path_maker
        self.assertNotRegex(path_maker.get_module_path(), '/umatobi/tests/')
        self.assertEqual(path_maker.get_module_path(), UMATOBI_MODULE_PATH)

    @patch('os.makedirs')
    @patch('os.path.isfile', return_value=False)
    @patch('os.path.isdir', return_value=False)
    @patch('shutil.copyfile')
    def test_set_simulation_schema(self, mock_copyfile, mock_isdir, mock_isfile, mock_makedirs):
        path_maker = self.path_maker
        simulation_dir_path = path_maker.get_simulation_dir_path()
        simulation_schema_path = path_maker.get_simulation_schema_path()

        with self.assertLogs('umatobi', level='INFO') as cm:
            simulation_schema_path = path_maker.set_simulation_schema()

        self.assertEqual(cm.output[0], f"INFO:umatobi:os.makedirs('{simulation_dir_path}')")
        self.assertEqual(cm.output[1],
                f"INFO:umatobi:shutil.copyfile(SIMULATION_SCHEMA_PATH={SIMULATION_SCHEMA_PATH}, simulation_schema_path={simulation_schema_path})")
        mock_isfile.assert_called_once_with(path_maker.get_simulation_schema_path())
        mock_isdir.assert_called_once_with(path_maker.get_simulation_dir_path())
        mock_makedirs.assert_called_once_with(path_maker.get_simulation_dir_path(), exist_ok=True)
        mock_copyfile.assert_called_once_with(SIMULATION_SCHEMA_PATH, simulation_schema_path)

    @patch('os.path.isfile', return_value=True)
    def test_set_simulation_schema_path(self, mock_isfile):
        path_maker = self.path_maker

        try:
            with self.assertLogs('umatobi', level='INFO') as cm:
                simulation_schema_path = path_maker.set_simulation_schema()
        except AssertionError as err:
            self.assertEqual(err.args[0], 'no logs of level INFO or higher triggered on umatobi')

        mock_isfile.assert_called_once_with(simulation_schema_path)

    def test_get_master_palm_txt_path(self):
        path_maker = self.path_maker
        self.assertEqual(
            path_maker.get_master_palm_txt_path(),
            os.path.join(SIMULATION_ROOT_PATH,
                         path_maker.simulation_time.get_y15s(),
                         MASTER_PALM_TXT))

    @patch('os.path.isdir', return_value=False)
    @patch('os.makedirs')
    def test_make_simulation_dir(self, mock_makedirs, mock_isdir):
        path_maker = self.path_maker
        simulation_dir_path = path_maker.get_simulation_dir_path()

        mock_isdir.assert_not_called()
        with self.assertLogs('umatobi', level='INFO') as cm:
            path_maker.make_simulation_dir()
        self.assertRegex(cm.output[0], fr"^INFO:umatobi:os.makedirs\('/.+/{RE_Y15S}'\)$")
        self.assertEqual(cm.output[0], f"INFO:umatobi:os.makedirs('{simulation_dir_path}')")
        mock_isdir.assert_called_once()
        mock_makedirs.assert_called_with(simulation_dir_path, exist_ok=True)

    @patch('os.path.isdir', return_value=True)
    @patch('os.makedirs')
    def test_make_simulation_dir_path(self, mock_makedirs, mock_isdir):
        path_maker = self.path_maker
        simulation_dir_path = path_maker.get_simulation_dir_path()

        mock_isdir.assert_not_called()

        path_maker.make_simulation_dir()

        mock_isdir.assert_called_once()
        mock_makedirs.assert_not_called()

if __name__ == '__main__':
    unittest.main()
