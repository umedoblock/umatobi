import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import simulator.sql
import lib

here = os.path.dirname(__file__)
test_schema_path = os.path.join(here, 'test.schema')
test_db_path = os.path.join(here, 'test.db')

class TestSQL(unittest.TestCase):
    def test_create_db_and_table(self):
        sql = simulator.sql.SQL(db_path=test_db_path,
                                schema_path=test_schema_path)
        sql.create_db()
        sql.create_table('test_table')

      # print(sql._create_table['test_table'])
        os.remove(test_db_path)

    def test_insert_and_select(self):
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
        sql.insert('test_table', d_insert)

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

        d_insert['id'] = 1 # auto increment
        for column, index in d.items():
            self.assertEqual(d_insert[column], d_selected[0][index])

        os.remove(test_db_path)

    def test_create_db_and_table_on_memory(self):
        sql = simulator.sql.SQL(db_path=':memory:',
                                schema_path=test_schema_path)
        sql.create_db()
        sql.create_table('test_table')

      # print(sql._create_table['test_table'])

if __name__ == '__main__':
    try:
        os.remove(test_db_path)
    except OSError as raiz:
        if raiz.args != (2, 'No such file or directory'):
            raise raiz

    unittest.main(exit=False)
