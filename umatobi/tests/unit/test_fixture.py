import unittest
import sys, datetime

from umatobi.tests import *
from umatobi.lib import *
from umatobi.simulator.core.key import Key
from umatobi.simulator.sql import SQL

pa = TEST_YAML_PATH.replace(ATAT_N, '1')
class FixtureTests(unittest.TestCase):

    YAML = {}

    @classmethod
    def setUpClass(cls):
        cls.start_up_orig = SimulationTime()
        set_simulation_schema(cls.start_up_orig)

        # yaml_path = 'tests/fixtures/test.yaml'
        cls.YAML = load_yaml(TEST_FIXTURES_PATH.replace(ATAT_N, ''))

        simulation_db_path = get_simulation_db_path(cls.start_up_orig)
        schema_path = get_simulation_schema_path(cls.start_up_orig)
        cls.simulation_db = SQL(db_path=simulation_db_path,
                                schema_path=schema_path)
        cls.simulation_db.create_db()

    @classmethod
    def tearDownClass(cls):
        cls.YAML = ''

        cls.simulation_db.close()
        cls.simulation_db.remove_db()

    def test_quentin_as_component(self):
        expected_schema_path, \
        expected_table_name, \
        expected_quentin_raw = \
            '../../simulator/simulation.schema', \
            'nodes', \
            {
                'id': '3',
                'now_iso8601': '2011-12-22T11:11:44.901234',
                'addr': '127.0.0.1:22222',
              # 'key': '0x' + '1' * Key.KEY_HEXES,
                'key': 'ERERERERERERERERERERERERERERERERERERERERERE=',
                'status': 'active'
            }

        schema_path, table_name, quentin_raw = FixtureTests.YAML['quentin']
        self.assertEqual(expected_schema_path, schema_path)
        self.assertEqual(expected_table_name, table_name)
        self.assertEqual(expected_quentin_raw, quentin_raw)

    def test_insert_nodes(self):
        expected_schema_path, \
        expected_table_name, \
        expected_quentin_raw = \
            '../../simulator/simulation.schema', \
            'nodes', \
            ({
                'id': '3',
                'now_iso8601': '2011-12-22T11:11:44.901234',
                'addr': '127.0.0.1:22222',
              # 'key': '0x' + '1' * Key.KEY_HEXES,
                'key': 'ERERERERERERERERERERERERERERERERERERERERERE=',
                'status': 'active'
            },)

        db = FixtureTests.simulation_db
        inserts_fixture(db, TEST_FIXTURES_PATH.replace(ATAT_N, ''),
                       'test_set_nodes')
      # select(self, table_name, select_columns='*', conditions=''):
        rows = db.select('clients', 'id,addr')
       #print('rows =')
       #print(rows)

if __name__ == '__main__':
    unittest.main()
