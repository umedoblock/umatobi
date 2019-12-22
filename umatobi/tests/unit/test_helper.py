# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import os
import unittest

from umatobi.lib import *
from umatobi.simulator.core.key import Key
from umatobi.simulator.sql import SQL

from umatobi.tests import *
from umatobi.tests.helper import *
from umatobi.tests.constants import *

class HelperTests(unittest.TestCase):

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

        db = HelperTests.simulation_db
        schema_parser, table_name, fixture = \
            inserts_fixture(db, replace_atat_n(''), 'test_set_nodes')
      # select(self, table_name, select_columns='*', conditions=''):
       #print('rows =')
       #print(rows)

#       self.assertEqual(schema_parser.schema_path, get_simulation_schema_path(HelperTests.start_up_orig))
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

        db = self.test_db
        for i in range(2):
            schema_parser, table_name, fixture = \
                    inserts_fixture(db, HelperTests.test_yaml_path,
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

if __name__ == '__main__':
    unittest.main()
