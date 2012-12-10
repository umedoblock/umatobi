import sys
import os
import time
import datetime
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import simulator.sql
import lib

here = os.path.dirname(__file__)
test_schema_path = os.path.join(here, 'test.schema')
test_db_path = os.path.join(here, 'test.db')

def remove_test_db():
    try:
        os.remove(test_db_path)
    except OSError as raiz:
        if raiz.args != (2, 'No such file or directory'):
            raise raiz

class TestSQL(unittest.TestCase):
    def tearDown(self):
        remove_test_db()

    def test_create_db_and_table(self):
        sql = simulator.sql.SQL(db_path=test_db_path,
                                schema_path=test_schema_path)
        sql.create_db()
        sql.create_table('test_table')

    def test_insert_and_select(self):
        s = datetime.datetime.now()
        sql = simulator.sql.SQL(db_path=test_db_path,
                                schema_path=test_schema_path)
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
        d_insert['now'] = lib.current_isoformat_time()
        e = datetime.datetime.now()
        d_insert['elapsed_time'] = lib.elapsed_time(e, s)
        sql.insert('test_table', d_insert)
        sql.commit()

      # d_select = {}
      # d_select['id'] = 1, d_select
        d_selected = sql.select('test_table')
        print('type(d_selected) =')
        print(type(d_selected))
        print('d_selected =')
        print(d_selected)

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

        sql = simulator.sql.SQL(db_path=test_db_path,
                                schema_path=test_schema_path)
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
        d_insert['now'] = lib.current_isoformat_time()
        e = datetime.datetime.now()
        d_insert['elapsed_time'] = lib.elapsed_time(e, s)
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
        t = time.time() + 1000
        d_update['now'] = lib.isoformat_time(t)
        e = datetime.datetime.now()
        d_update['elapsed_time'] = lib.elapsed_time(e, s)

        d_where = {'id': 1}
        sql.update('test_table', d_update, d_where)

        d_selected = sql.select('test_table')

        print('d_selected =', d_selected)
        for column, index in d.items():
            if column == 'id':
                self.assertEqual(d_insert[column], d_selected[0][index])
                continue
            self.assertEqual(d_update[column], d_selected[0][index])
            self.assertNotEqual(d_insert[column], d_selected[0][index])

    def test_create_db_and_table_on_memory(self):
        sql = simulator.sql.SQL(db_path=':memory:',
                                schema_path=test_schema_path)
        sql.create_db()
        sql.create_table('test_table')

      # print(sql._create_table['test_table'])

if __name__ == '__main__':
    remove_test_db()
    unittest.main(exit=False)
