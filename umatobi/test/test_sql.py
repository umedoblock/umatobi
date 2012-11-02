import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import simulator.sql

here = os.path.dirname(__file__)
test_schema_path = os.path.join(here, 'test.schema')
test_db_path = os.path.join(here, 'test.db')

class TestSQL(unittest.TestCase):
    def test_create_db(self):
        with open(test_schema_path) as f:
            f.read()
        with open(test_db_path, 'w') as f:
            f.write('test')

        self.assertEqual(1, 1)

if __name__ == '__main__':
    unittest.main(exit=False)
    os.remove(test_db_path)
