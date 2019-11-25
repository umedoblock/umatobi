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

from umatobi.tests import *
from umatobi.simulator.sql import SQL
from umatobi import lib

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

class SQLTests(unittest.TestCase):

    def deleteTestDb(self):
        if os.path.isfile(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)

    def setUp(self):
        sql = SQL(db_path=TEST_DB_PATH, schema_path=TEST_SCHEMA_PATH)
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

    def test_construct_insert_by_dict(self):
        pass

    def test___init__(self):
        pass

    def test___init___schema_is_True_by_db_path1(self):
        sql = SQL(db_path='', schema_path=TEST_SCHEMA_PATH)
        self.assertTrue(sql._schema)
        self.assertIsInstance(sql._schema, configparser.ConfigParser)
        self.assertTrue(sql.closed())

    def test___init___schema_is_True_by_db_path2(self):
        sql = SQL(schema_path=TEST_SCHEMA_PATH)
        self.assertTrue(sql._schema)
        self.assertIsInstance(sql._schema, configparser.ConfigParser)
        self.assertTrue(sql.closed())

    def test___init___fail_by_schema_path_not_exist(self):
        sql = SQL(db_path=TEST_DB_PATH, schema_path='/not/exist/file')
        self.assertFalse(sql._schema)
        self.assertTrue(sql.closed())

    def test___init___fail_by_schema_path1(self):
        sql = SQL(db_path=TEST_DB_PATH, schema_path='')
        self.assertFalse(sql._schema)
        self.assertTrue(sql.closed())

    def test___init___fail_by_schema_path2(self):
        sql = SQL(db_path=TEST_DB_PATH)
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

        sql.read_schema(TEST_SCHEMA_PATH)
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

        sql.read_schema(TEST_SCHEMA_PATH)
        self.assertEqual(sql.schema_path, TEST_SCHEMA_PATH)
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
        sql = SQL(db_path='fixture.db', schema_path=TEST_SCHEMA_PATH)
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
        sql = SQL(db_path=':memory:', schema_path=TEST_SCHEMA_PATH)
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
        sql = SQL(db_path=':memory:', schema_path=TEST_SCHEMA_PATH)
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
        sql = SQL(db_path=not_found_path, schema_path=TEST_SCHEMA_PATH)
        self.assertTrue(sql._schema)
        self.assertTrue(sql.closed())

        with self.assertLogs('umatobi', level='INFO') as cm:
            with patch('umatobi.simulator.sql.os.path.isfile',
                        return_value=False) as mock_isfile:
                self.assertFalse(os.path.isfile(sql.db_path))
                sql.remove_db()
                self.assertFalse(os.path.isfile(sql.db_path))
        self.assertTrue(sql.closed())
        mock_isfile.assert_called_with(sql.db_path)
        self.assertRegex(cm.output[0], r'INFO:umatobi:SQL\(db_path="{}", schema_path=".+/test.schema"\) not found db_path={}\.$'.format(not_found_path, not_found_path))

    def test_create_table(self):
        sql = SQL(db_path=':memory:', schema_path=TEST_SCHEMA_PATH)
        sql.create_db()

        self.assertNotIn('test_table', sql.get_table_names())
        sql.create_table('test_table')
        self.assertIn('test_table', sql.get_table_names())

    def test_create_table_fail_by__conn_is_None(self):
        sql = SQL(db_path=':memory:', schema_path=TEST_SCHEMA_PATH)

        with self.assertRaises(RuntimeError) as assert_error:
            sql.create_table('test_table')
        args = assert_error.exception.args
        self.assertEqual(args[0], 'you must call create_db() before call create_table().')

    def test_create_table_fail_by__schema_is_None(self):
        sql = SQL(db_path=':memory:')
        sql.create_db()

        with self.assertLogs('umatobi', level='INFO') as cm:
            with self.assertRaises(TypeError) as assert_error:
                sql.create_table('test_table')
        args = assert_error.exception.args

        self.assertEqual(cm.output[0], f'INFO:umatobi:{sql}.create_table(table_name=test_table)')
        self.assertEqual(cm.output[1], f'ERROR:umatobi:os.path.isfile(schema_path=\'{sql.schema_path}\') must return True and')
        self.assertEqual(cm.output[2], 'ERROR:umatobi:must call sql.read_schema()')
        self.assertEqual(args[0], "'NoneType' object is not subscriptable")

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
        memory_db = SQL(db_path=':memory:', schema_path=TEST_SCHEMA_PATH)
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
