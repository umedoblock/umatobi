import unittest
import sys, datetime

from umatobi.tests import *
from umatobi.lib import *
from umatobi.simulator.core.key import Key

pa = TEST_YAML_PATH.replace(ATAT_N, '1')
class FixtureTests(unittest.TestCase):

    YAML = {}

    @classmethod
    def setUpClass(cls):
        # yaml_path = 'tests/fixtures/test.yaml'
        cls.YAML = load_yaml(TEST_FIXTURES_PATH.replace(ATAT_N, ''))

    @classmethod
    def tearDownClass(cls):
        cls.YAML = ''

    def test_quentin_as_component(self):
        expected_schema_path, \
        expected_table_name, \
        expected_quentin_raw = \
            '../simulator/simulation.schema', \
            'nodes', \
            {
                'id': '3',
                'now_iso8601': '2011-12-22T11:11:44.901234',
                'addr': '127.0.0.1:22222',
                'key': '0x' + '1' * Key.KEY_HEXES,
                'status': 'active'
            }

        schema_path, table_name, quentin_raw = FixtureTests.YAML['quentin']
        self.assertEqual(expected_schema_path, schema_path)
        self.assertEqual(expected_table_name, table_name)
        self.assertEqual(expected_quentin_raw, quentin_raw)

if __name__ == '__main__':
    unittest.main()
