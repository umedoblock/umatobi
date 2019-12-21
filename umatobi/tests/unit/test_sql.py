# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import sys
import os
import time
import datetime
import unittest
from unittest.mock import MagicMock
import sqlite3

from umatobi.simulator.core.key import Key

from umatobi.tests import *
from umatobi.simulator.sql import *

class SimulatorSQLTests(unittest.TestCase):

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

def insert_test_table_n_records(db, n_records):
    s = datetime.datetime.now()
    inserts = [None] * n_records
    for i in range(n_records):
        test = {}
        test['id'] = None # integer primary key
                          # autoincrement unique not null
        test['val_null'] = None
        test['val_integer'] = i * 1000
        test['val_real'] = i * 111.111
        test['val_text'] = 't' * (i + 1)
        test['val_blob'] = b'bytes' * (i + 1)
        test['now'] = SimulationTime().get_y15s()
        e = datetime.datetime.now()
        test['elapsed_time'] = (e - s).total_seconds()
        test['iso8601'] = None
        db.insert('test_table', test)
        inserts[i] = test
    #   print('[{}]'.format(i))
    db.commit()
    for i in range(n_records):
        inserts[i]['id'] = i + 1
    return inserts

class SchemaParserTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.simulation_time = SimulationTime()
#       cls.path_maker = PathMaker(cls.simulation_time)
#       cls.path_maker.set_simulation_schema()

    def assert_simulation_schema_path(self, inspected_path):
        self.assert_simulation_dir_path(inspected_path)
        self.assertRegex(inspected_path, f"{SIMULATION_SCHEMA}$")

    def assert_simulation_dir_path(self, dir_path):
        self.assertNotRegex(dir_path, ATAT_SIMULATION_TIME)
        self.assertRegex(dir_path, RE_Y15S)

    def setUp(self):
        self.simulation_time = SchemaParserTests.simulation_time
        self.path_maker = PathMaker(self.simulation_time)

    def tearDown(self):
        shutil.rmtree(os.path.dirname(self.path_maker.get_master_palm_txt_path()), ignore_errors=True)

    def test___init__(self):
        simulation_time = self.simulation_time
        simulation_schema_path = self.path_maker.set_simulation_schema()
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

                # milli seconds
                'elapsed_time':    converter_integer,

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

        simulation_schema_path = self.path_maker.set_simulation_schema()
        self.assert_simulation_schema_path(simulation_schema_path)

        schema_parser = SchemaParser(simulation_schema_path)
        self.assertEqual(schema_parser.schema_path, simulation_schema_path)
        self.assertSequenceEqual(schema_parser.get_table_names(),
                           tuple(expected_items.keys()))

    def test_get_table_names_from_schema(self):
        simulation_schema_path = self.path_maker.set_simulation_schema()
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
                'id', 'elapsed_time', 'pickle'
            ),
            'nodes': (
                'id', 'elapsed_time', 'addr', 'key', 'status'
            ),
        }

        simulation_schema_path = self.path_maker.set_simulation_schema()
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
elapsed_time: 15382
addr: 127.0.0.1:22222
key: qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqo=
status: active
'''
# >>> base64.b64encode(b'\xaa\xaa\xaa')
# b'qqqq'
# >>> base64.b64decode(b'qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqo=')
# b'\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa'

        simulation_schema_path = self.path_maker.set_simulation_schema()
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
        self.assertEqual(records.nodes['elapsed_time'], 15382)
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

class SQLTests(unittest.TestCase):

    def deleteTestDb(self):
        if os.path.isfile(TESTS_DB_PATH):
            os.remove(TESTS_DB_PATH)

    def setUp(self):
        sql = SQL(db_path=TESTS_DB_PATH, schema_path=TESTS_SCHEMA_PATH)
        self.assertTrue(sql._schema)
        self.assertIsInstance(sql._schema, configparser.ConfigParser)
        self.assertFalse(os.path.isfile(sql.db_path))
        self.assertTrue(sql.closed())
        sql.create_db()
        self.assertFalse(sql.closed())
        self.assertTrue(os.path.isfile(sql.db_path))
        sql.create_table('test_table')

        self.sql = sql

        self.addCleanup(self.deleteTestDb)

    def test_make_question_marks(self):
        L = ((1, '(?)'), (2, '(?, ?)'),
            (18, '(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'))

        for n_questions, expected_question_marks in L:
            self.assertEqual(SQL.make_question_marks(n_questions),
                             expected_question_marks)

    def test_make_question_marks_fail_by_invalid_num(self):
        for n_questions in (1.0, '1'):
            with self.assertRaises(TypeError) as cm:
                SQL.make_question_marks(n_questions)
            err_args = cm.exception.args
            self.assertEqual(err_args[0], f'make_question_marks(="{n_questions}") argument must be an integer.')

        for n_questions in (0, -1):
            with self.assertRaises(ValueError) as cm:
                SQL.make_question_marks(n_questions)
            err_args = cm.exception.args
            self.assertEqual(err_args[0], f'n_questions(={n_questions}) must be greater than or equal to one.')

    def test_construct_insert_by_dict(self):
        pass

    def test___init__(self):
        pass

    def test___init___schema_is_True_by_db_path1(self):
        sql = SQL(db_path='', schema_path=TESTS_SCHEMA_PATH)
        self.assertTrue(sql._schema)
        self.assertIsInstance(sql._schema, configparser.ConfigParser)
        self.assertTrue(sql.closed())

    def test___init___schema_is_True_by_db_path2(self):
        sql = SQL(schema_path=TESTS_SCHEMA_PATH)
        self.assertTrue(sql._schema)
        self.assertIsInstance(sql._schema, configparser.ConfigParser)
        self.assertTrue(sql.closed())

    def test___init___fail_by_schema_path_not_exist(self):
        sql = SQL(db_path=TESTS_DB_PATH, schema_path='/not/exist/file')
        self.assertFalse(sql._schema)
        self.assertTrue(sql.closed())

    def test___init___fail_by_schema_path1(self):
        sql = SQL(db_path=TESTS_DB_PATH, schema_path='')
        self.assertFalse(sql._schema)
        self.assertTrue(sql.closed())

    def test___init___fail_by_schema_path2(self):
        sql = SQL(db_path=TESTS_DB_PATH)
        self.assertFalse(sql._schema)
        self.assertTrue(sql.closed())

    def test_read_schema(self):
        sql = SQL(db_path=':memory:')
        self.assertEqual(sql.db_path, ':memory:')
        self.assertFalse(os.path.isfile(sql.db_path))
        self.assertEqual(sql.schema_path, '')

        self.assertIsNone(sql._conn)
        self.assertIsNone(sql._cur)
        self.assertDictEqual(sql._create_table, {})

        self.assertIsNone(sql._schema)
        self.assertTrue(sql.closed())

        sql.read_schema(TESTS_SCHEMA_PATH)
        self.assertIsNotNone(sql._schema)
        self.assertTrue(sql.closed())
        self.assertFalse(os.path.isfile(sql.db_path))

    def test_read_schema_override(self):
        sql = SQL(db_path=':memory:', schema_path='/not/exist/schema')
        self.assertEqual(sql.db_path, ':memory:')
        self.assertFalse(os.path.isfile(sql.db_path))
        self.assertEqual(sql.schema_path, '/not/exist/schema')

        self.assertIsNone(sql._conn)
        self.assertIsNone(sql._cur)
        self.assertDictEqual(sql._create_table, {})

        self.assertIsNone(sql._schema)
        self.assertTrue(sql.closed())

        sql.read_schema(TESTS_SCHEMA_PATH)
        self.assertEqual(sql.schema_path, TESTS_SCHEMA_PATH)
        self.assertIsNotNone(sql._schema)
        self.assertTrue(sql.closed())

    def test_read_schema_fail_by_not_found_schema_path(self):
        sql = SQL(db_path=':memory:', schema_path='/not/found/schema/path')
        self.assertEqual(sql.db_path, ':memory:')
        self.assertFalse(os.path.isfile(sql.db_path))
        self.assertEqual(sql.schema_path, '/not/found/schema/path')

        self.assertIsNone(sql._conn)
        self.assertIsNone(sql._cur)
        self.assertDictEqual(sql._create_table, {})

        self.assertIsNone(sql._schema)
        self.assertTrue(sql.closed())

        with self.assertRaises(FileNotFoundError) as assert_error:
            sql.read_schema()
        args = assert_error.exception.args
        self.assertEqual(args[0], 2)
        self.assertEqual(args[1], 'No such file or directory')

    def test_access_db(self):
        pass

    def test_create_db_and_table(self):
        sql = self.sql

    @patch.object(sqlite3, 'connect')
    def test_create_db_db_dir_name_empty(self, mock_sqlite3_connect):
        sql = SQL(db_path='fixture.db', schema_path=TESTS_SCHEMA_PATH)
        self.assertTrue(sql._schema)
        self.assertIsInstance(sql._schema, configparser.ConfigParser)
        self.assertFalse(os.path.isfile(sql.db_path))
        self.assertTrue(sql.closed())
        sql.create_db()
        self.assertFalse(sql.closed())
        mock_sqlite3_connect.called_with(sql.db_path)

        self.assertIsInstance(sql._conn, MagicMock)
        self.assertEqual(sql._conn.row_factory, sqlite3.Row)
        self.assertIsInstance(sql._cur, MagicMock)

    def test_create_db_and_table_on_memory(self):
        sql = SQL(db_path=':memory:', schema_path=TESTS_SCHEMA_PATH)
        self.assertTrue(sql._schema)
        self.assertIsInstance(sql._schema, configparser.ConfigParser)
        self.assertFalse(os.path.isfile(sql.db_path))
        self.assertTrue(sql.closed())
        sql.create_db()
        self.assertFalse(sql.closed())
        self.assertFalse(os.path.isfile(sql.db_path))

        sql.create_table('test_table')

      # print(sql._create_table['test_table'])

        self.assertFalse(os.path.isfile(sql.db_path))
        sql.remove_db()
        self.assertFalse(sql.closed())
        self.assertFalse(os.path.isfile(sql.db_path))

    def test_remove_db(self):
        sql = self.sql

        self.assertTrue(os.path.isfile(sql.db_path))
        sql.remove_db()
        self.assertFalse(os.path.isfile(sql.db_path))
        self.assertFalse(sql.closed())

    def test_remove_db_memory(self):
        sql = SQL(db_path=':memory:', schema_path=TESTS_SCHEMA_PATH)
        self.assertTrue(sql._schema)
        self.assertIsInstance(sql._schema, configparser.ConfigParser)
        self.assertFalse(os.path.isfile(sql.db_path))
        sql.create_db()
        self.assertFalse(os.path.isfile(sql.db_path))
        self.assertFalse(sql.closed())

        with self.assertRaises(AssertionError) as err:
            with self.assertLogs('umatobi', level='INFO') as cm:
                sql.remove_db()
            self.assertFalse(os.path.isfile(sql.db_path))
        self.assertFalse(sql.closed())
        args = err.exception.args
        self.assertEqual('no logs of level INFO or higher triggered on umatobi', args[0])

    def test_remove_db_not_memory(self):
        not_found_path = '/not/found/db_path'
        sql = SQL(db_path=not_found_path, schema_path=TESTS_SCHEMA_PATH)
        self.assertTrue(sql._schema)
        self.assertTrue(sql.closed())

        with self.assertRaises(RuntimeError) as err:
            with self.assertLogs('umatobi', level='ERROR') as cm:
                with patch('umatobi.simulator.sql.os.path.isfile',
                            return_value=False) as mock_isfile:
                    self.assertFalse(os.path.isfile(sql.db_path))
                    sql.remove_db()
                    self.assertFalse(os.path.isfile(sql.db_path))
        self.assertTrue(sql.closed())
        mock_isfile.assert_called_with(sql.db_path)
        args = err.exception.args
        self.assertEqual(cm.output[0], f'ERROR:umatobi:{sql} not found db_path={sql.db_path}.')
        self.assertEqual(args[0], f'{sql} not found db_path={sql.db_path}.')

    def test_create_table(self):
        sql = SQL(db_path=':memory:', schema_path=TESTS_SCHEMA_PATH)
        sql.create_db()

        self.assertNotIn('test_table', sql.get_table_names())
        sql.create_table('test_table')
        self.assertIn('test_table', sql.get_table_names())

    def test_create_table_fail_by__conn_is_None(self):
        sql = SQL(db_path=':memory:', schema_path=TESTS_SCHEMA_PATH)

        with self.assertRaises(RuntimeError) as assert_error:
            sql.create_table('test_table')
        args = assert_error.exception.args
        self.assertEqual(args[0], 'you must call create_db() before call create_table().')

    def test_create_table_fail_by__schema_is_None(self):
        sql = SQL(db_path=':memory:')
        sql.create_db()

        with self.assertLogs('umatobi', level='INFO') as cm:
            with self.assertRaises(RuntimeError) as assert_error:
                sql.create_table('test_table')
        args = assert_error.exception.args

        self.assertEqual(cm.output[0], f'INFO:umatobi:{sql}.create_table(table_name="test_table")')
        self.assertEqual(cm.output[1], f'ERROR:umatobi:os.path.isfile(schema_path="{sql.schema_path}") must return True and')
        self.assertEqual(cm.output[2], 'ERROR:umatobi:must call sql.read_schema()')
        self.assertEqual(args[0], f'{sql}._schema is None.')

    def test_select_one(self):
        pass

    def test_drop_table(self):
        pass

    def test_init_table(self):
        pass

    def test_take_table(self):
        db = self.sql

        n_records = 100
        inserts = insert_test_table_n_records(db, n_records)

#       print('-------------------------------------')
        records = \
            db.select('test_table', conditions='order by id')
#       print('len(records)=', len(records))
#       print('records=', records)
#       print(records)
#       print('-------------------------------------')
        memory_db = SQL(db_path=':memory:', schema_path=TESTS_SCHEMA_PATH)
        self.assertTrue(memory_db._schema)
        self.assertIsInstance(memory_db._schema, configparser.ConfigParser)
        self.assertFalse(os.path.isfile(memory_db.db_path))
        self.assertTrue(memory_db.closed())

        memory_db.create_db()
        self.assertFalse(memory_db.closed())
        self.assertFalse(os.path.isfile(memory_db.db_path))
        self.assertFalse(memory_db.closed())

        memory_db.take_table(db, 'test_table')

        db.remove_db()
        self.assertFalse(os.path.isfile(db.db_path))

        memory_records = \
            memory_db.select('test_table', conditions='order by id')
#       print('len(memory_records)=', len(memory_records))
#       print('memory_records =')
#       print(memory_records)
#       print('-------------------------------------')
        for i in range(n_records):
#           print(i)
#           print(dir(memory_records[i]))
            self.assertEqual(list(inserts[i].keys()).sort(), \
                             memory_records[i].keys().sort())
            for key in memory_records[i].keys():
                self.assertEqual(inserts[i][key], memory_records[i][key])
        self.assertFalse(os.path.isfile(memory_db.db_path))
        memory_db.remove_db()
        self.assertFalse(os.path.isfile(memory_db.db_path))
        self.assertFalse(db.closed())

    def test_take_db(self):
        pass

    def test_commit(self):
        pass

    def test_execute(self):
        pass

    def test_close_and_closed(self):
        db = self.sql

        self.assertFalse(db.closed())
        db.close()
        self.assertTrue(db.closed())

    def test_inserts(self):
        s = datetime.datetime.now()
        simulation_time = SimulationTime()
        sql = self.sql

        e = datetime.datetime.now()
        d_expected = [{
            'id': 0,
            'val_null': None,
            'val_integer': 111,
            'val_real': 11.1,
            'val_text': 'text',
            'val_blob': b'bytes',
            'now': str(simulation_time),
            'elapsed_time': (e - s).total_seconds(),
            'iso8601': str(simulation_time),
        }, {
            'id': 1,
            'val_null': None,
            'val_integer': 222,
            'val_real': 22.2,
            'val_text': 'text',
            'val_blob': b'bytes',
            'now': str(simulation_time),
            'elapsed_time': (e - s).total_seconds(),
            'iso8601': str(simulation_time),
        }]
        sql.inserts_via_dict('test_table', d_expected)
        sql.commit()

      # d_select = {}
      # d_select['id'] = 1, d_select
        d_selected = sql.select('test_table')
       #print('type(d_selected) =')
       #print(type(d_selected))
       #print('d_selected =')
       #print(d_selected)
       #tuple(tup) for tup in
        L = []
        for obj in d_selected:
       #    print('obj =', obj)
       #    print('tuple(obj) =', tuple(obj))
            L.append(tuple(obj))
       #print('--')

        L_expected = []
        for obj in d_expected:
       #    print('obj2 =', obj)
       #    print('tuple(obj2.values()) =', tuple(obj.values()))
            L_expected.append(tuple(obj.values()))
       #print('--')

        self.assertEqual(L, L_expected)

    def test_insert_and_select(self):
        s = datetime.datetime.now()
        simulation_time = SimulationTime()
        sql = self.sql

        d_insert = {}
        d_insert['id'] = None # integer primary key
                              # autoincrement unique not null
        d_insert['val_null'] = None
        d_insert['val_integer'] = 3
        d_insert['val_real'] = 10.0
        d_insert['val_text'] = 'text'
        d_insert['val_blob'] = b'bytes'
        d_insert['now'] = SimulationTime().get_y15s()
        e = datetime.datetime.now()
        d_insert['elapsed_time'] = (e - s).total_seconds()
        d_insert['iso8601'] = str(simulation_time)
        sql.insert('test_table', d_insert)
        sql.commit()

      # d_select = {}
      # d_select['id'] = 1, d_select
        d_selected = sql.select('test_table')
      # print('type(d_selected) =')
      # print(type(d_selected))
      # print('d_selected =')
      # print(d_selected)

        d = sql.get_dict_of_columns('test_table')

        d_insert['id'] = 1 # auto increment
        for column, index in d.items():
            self.assertEqual(d_insert[column], d_selected[0][index])

    def test_insert_and_insert(self):
        s = datetime.datetime.now()

        sql = self.sql

        d = sql.get_dict_of_columns('test_table')

        d_insert = {}
        d_insert['id'] = None # integer primary key
                              # autoincrement unique not null
        d_insert['val_null'] = None
        d_insert['val_integer'] = 3
        d_insert['val_real'] = 10.0
        d_insert['val_text'] = 'text'
        d_insert['val_blob'] = b'bytes'
        d_insert['now'] = SimulationTime().get_y15s()
        e = SimulationTime.now()
        d_insert['elapsed_time'] = (e - s).total_seconds()
        d_insert['iso8601'] = str(SimulationTime())
        sql.insert('test_table', d_insert)
        sql.commit()

        d_selected = sql.select('test_table')

        d_insert['id'] = 1
        for column, index in d.items():
            self.assertEqual(d_insert[column], d_selected[0][index])
        self.assertEqual(len(d_insert.keys()), len(d_selected[0]))

        d_update = {}
        d_update['val_null'] = 'None None'
        d_update['val_integer'] = 30
        d_update['val_real'] = 100.0
        d_update['val_text'] = 'text text'
        d_update['val_blob'] = b'bytes bytes'
        now = datetime.datetime.now()
        t = now + datetime.timedelta(0, 1000, 0)
        d_update['now'] = SimulationTime(t).get_y15s()
        e = datetime.datetime.now()
        d_update['elapsed_time'] = (e - s).total_seconds()
        simulation_time = SimulationTime()
        d_update['iso8601'] = str(simulation_time)

        d_update['id'] = 1
        with self.assertRaises(sqlite3.IntegrityError) as raiz:
            sql.insert('test_table', d_update)
        args = raiz.exception.args
        self.assertEqual('UNIQUE constraint failed: test_table.id', args[0])

    def test_update_and_select(self):
        s = datetime.datetime.now()

        sql = self.sql

        d = sql.get_dict_of_columns('test_table')

        d_insert = {}
        d_insert['id'] = None # integer primary key
                              # autoincrement unique not null
        d_insert['val_null'] = None
        d_insert['val_integer'] = 3
        d_insert['val_real'] = 10.0
        d_insert['val_text'] = 'text'
        d_insert['val_blob'] = b'bytes'
        d_insert['iso8601'] = None
        s = datetime.datetime.now()
        now = s
        d_insert['now'] = SimulationTime(now).get_y15s()
        e = s + datetime.timedelta(0, 100, 0)
        d_insert['elapsed_time'] = (e - s).total_seconds()
        sql.insert('test_table', d_insert)
        sql.commit()

        d_selected = sql.select('test_table')

        d_insert['id'] = 1
        for column, index in d.items():
            self.assertEqual(d_insert[column], d_selected[0][index])

        d_update = {}
        d_update['val_null'] = 'None None'
        d_update['val_integer'] = 30
        d_update['val_real'] = 100.0
        d_update['val_text'] = 'text text'
        d_update['val_blob'] = b'bytes bytes'
        d_update['now'] = SimulationTime(now + datetime.timedelta(0, 200)).get_y15s()
        e = s + datetime.timedelta(0, 200, 0)
        d_update['elapsed_time'] = (e - s).total_seconds()
        updated_simulation_time = SimulationTime()
        d_update['iso8601'] = str(updated_simulation_time)

        d_where = {'id': 1}
        sql.update('test_table', d_update, d_where)

        d_selected = sql.select('test_table', conditions='where id = 1')

        self.assertNotEqual(d_update, d_selected)
        for column, index in d.items():
            if column == 'id':
                self.assertEqual(d_insert[column], d_selected[0][index])
                continue
          # print(d_update[column], ',', d_selected[0][index])
          # print(d_insert[column], ',', d_selected[0][index])
          # print()
            self.assertEqual(d_update[column], d_selected[0][index])
            self.assertNotEqual(d_insert[column], d_selected[0][index])

    def test_update_None(self):
        s = datetime.datetime.now()

        sql = self.sql

        d = sql.get_dict_of_columns('test_table')

        d_insert = {}
        d_insert['id'] = None # integer primary key
                              # autoincrement unique not null
        d_insert['val_text'] = None
        sql.insert('test_table', d_insert)
        sql.commit()

        d_selected = sql.select('test_table')

        d_insert['id'] = 1
        for column, index in d.items():
            if not column in d_insert:
                continue
            self.assertEqual(d_insert[column], d_selected[0][index])

        d_update = {
            'val_text': 'None',
        }

        d_where = {'id': 1}
        sql.update('test_table', d_update, d_where)

        d_selected = sql.select('test_table', conditions='where id = 1')

        self.assertNotEqual(d_update, d_selected)
        for column, index in d.items():
          # print()
          # print(f'column={column}, index={index}')
            if column == 'id':
                self.assertEqual(d_insert[column], d_selected[0][index])
                continue
          # print(f'not column{column} in d_insert{tuple(d_insert)} is {not column in tuple(d_insert)}')
            if not column in d_update:
                continue
            self.assertEqual(d_update[column], d_selected[0][index])
            self.assertNotEqual(d_insert[column], d_selected[0][index])

    def test_select(self):
        pass

    def test_get_table_names(self):
        pass

    def test_get_table_schema(self):
        pass

    def test_get_column_names(self):
        sql = self.sql

        expected_column_names = (
            'id', 'val_null', 'val_integer', 'val_real', 'val_text',
            'val_blob', 'now', 'elapsed_time', 'iso8601'
        )
        self.assertEqual(sql.get_column_names('test_table'),
                         expected_column_names)

    def test_get_dict_of_columns(self):
        sql = self.sql

        d = sql.get_dict_of_columns('test_table')

        expected_d = {
            'id':           0,
            'val_null':     1,
            'val_integer':  2,
            'val_real':     3,
            'val_text':     4,
            'val_blob':     5,
            'now':          6,
            'elapsed_time': 7,
            'iso8601':      8,
        }
        self.assertEqual(d, expected_d)

    def test___str__(self):
        pass

if __name__ == '__main__':
    unittest.main(exit=False)
