import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import simulator.sql

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

    def test_create_db_and_table_on_memory(self):
        sql = simulator.sql.SQL(db_path=':memory:',
                                schema_path=test_schema_path)
        sql.create_db()
        sql.create_table('test_table')

      # print(sql._create_table['test_table'])

if __name__ == '__main__':
    unittest.main(exit=False)
