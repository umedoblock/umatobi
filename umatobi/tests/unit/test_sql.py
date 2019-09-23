import sys
import os
import time
import datetime
import unittest
import sqlite3

from umatobi.tests import *
from umatobi.simulator.sql import SQL
from umatobi import lib

def remove_test_db():
    try:
        os.remove(TEST_DB_PATH)
    except OSError as raiz:
        if raiz.args != (2, 'No such file or directory'):
            raise raiz

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
        db.insert('test_table', test)
        inserts[i] = test
    #   print('[{}]'.format(i))
    db.commit()
    for i in range(n_records):
        inserts[i]['id'] = i + 1
    return inserts

class SQLTests(unittest.TestCase):
    def tearDown(self):
        remove_test_db()

    def test_create_db_and_table(self):
        sql = SQL(db_path=TEST_DB_PATH, schema_path=TEST_SCHEMA_PATH)
        sql.create_db()
        sql.create_table('test_table')

    def test_remove_db(self):
        sql = SQL(db_path=TEST_DB_PATH, schema_path=TEST_SCHEMA_PATH)
        sql.create_db()

        self.assertTrue(os.path.isfile(sql.db_path))
        sql.remove_db()
        self.assertFalse(os.path.isfile(sql.db_path))

    def test_remove_db_memory(self):
        sql = SQL(db_path=':memory:', schema_path=TEST_SCHEMA_PATH)
        sql.create_db()
        self.assertFalse(os.path.isfile(sql.db_path))

        with self.assertRaises(AssertionError) as err:
            with self.assertLogs('umatobi', level='INFO') as cm:
                sql.remove_db()
            self.assertFalse(os.path.isfile(sql.db_path))
        args = err.exception.args
        self.assertEqual('no logs of level INFO or higher triggered on umatobi', args[0])

    def test_remove_db_not_memory(self):
        not_found_path = '/not/found/db_path'
        sql = SQL(db_path=not_found_path, schema_path=TEST_SCHEMA_PATH)

        with self.assertLogs('umatobi', level='INFO') as cm:
            with patch('umatobi.simulator.sql.os.path.isfile',
                        return_value=False) as mock_isfile:
                self.assertFalse(os.path.isfile(sql.db_path))
                sql.remove_db()
                self.assertFalse(os.path.isfile(sql.db_path))
        mock_isfile.assert_called_with(sql.db_path)
        self.assertRegex(cm.output[0], r'INFO:umatobi:SQL\(db_path="{}", schema_path=".+/test.schema"\) not found db_path={}\.$'.format(not_found_path, not_found_path))

    def test_insert_and_select(self):
        s = datetime.datetime.now()
        sql = SQL(db_path=TEST_DB_PATH, schema_path=TEST_SCHEMA_PATH)
        sql.create_db()
        sql.create_table('test_table')

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
        sql.insert('test_table', d_insert)
        sql.commit()

      # d_select = {}
      # d_select['id'] = 1, d_select
        d_selected = sql.select('test_table')
      # print('type(d_selected) =')
      # print(type(d_selected))
      # print('d_selected =')
      # print(d_selected)

        d = {}
        d['id'] = 0
        d['val_null'] = 1
        d['val_integer'] = 2
        d['val_real'] = 3
        d['val_text'] = 4
        d['val_blob'] = 5
        d['now'] = 6
        d['elapsed_time'] = 7

        d_insert['id'] = 1 # auto increment
        for column, index in d.items():
            self.assertEqual(d_insert[column], d_selected[0][index])

    def test_take_table(self):
        db = SQL(db_path=TEST_DB_PATH, schema_path=TEST_SCHEMA_PATH)
        db.create_db()
        db.create_table('test_table')

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
        memory_db.create_db()
        memory_db.take_table(db, 'test_table')

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

    def test_insert_and_insert(self):
        s = datetime.datetime.now()
        d = {}
        d['id'] = 0
        d['val_null'] = 1
        d['val_integer'] = 2
        d['val_real'] = 3
        d['val_text'] = 4
        d['val_blob'] = 5
        d['now'] = 6
        d['elapsed_time'] = 7

        sql = SQL(db_path=TEST_DB_PATH, schema_path=TEST_SCHEMA_PATH)
        sql.create_db()
        sql.create_table('test_table')

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
        now = datetime.datetime.now()
        t = now + datetime.timedelta(0, 1000, 0)
        d_update['now'] = SimulationTime(t).get_y15s()
        e = datetime.datetime.now()
        d_update['elapsed_time'] = (e - s).total_seconds()

        d_update['id'] = 1
        with self.assertRaises(sqlite3.IntegrityError) as raiz:
            sql.insert('test_table', d_update)
        args = raiz.exception.args
        self.assertEqual('UNIQUE constraint failed: test_table.id', args[0])

    def test_update_and_select(self):
        s = datetime.datetime.now()
        d = {}
        d['id'] = 0
        d['val_null'] = 1
        d['val_integer'] = 2
        d['val_real'] = 3
        d['val_text'] = 4
        d['val_blob'] = 5
        d['now'] = 6
        d['elapsed_time'] = 7

        sql = SQL(db_path=TEST_DB_PATH, schema_path=TEST_SCHEMA_PATH)
        sql.create_db()
        sql.create_table('test_table')

        d_insert = {}
        d_insert['id'] = None # integer primary key
                              # autoincrement unique not null
        d_insert['val_null'] = None
        d_insert['val_integer'] = 3
        d_insert['val_real'] = 10.0
        d_insert['val_text'] = 'text'
        d_insert['val_blob'] = b'bytes'
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

    def test_create_db_and_table_on_memory(self):
        sql = SQL(db_path=':memory:', schema_path=TEST_SCHEMA_PATH)
        sql.create_db()
        sql.create_table('test_table')

      # print(sql._create_table['test_table'])

if __name__ == '__main__':
    remove_test_db()
    unittest.main(exit=False)
