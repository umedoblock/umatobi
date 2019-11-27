# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import unittest
from unittest.mock import call

import umatobi
from umatobi.tests import *
from umatobi.lib import *
from umatobi.simulator.sql import SQL
from umatobi.tools.make_simulation_db import *

class MakeSimulationDbTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.start_up_orig = SimulationTime()
        set_simulation_schema(cls.start_up_orig)

        simulation_db_path = get_simulation_db_path(cls.start_up_orig)
        schema_path = get_simulation_schema_path(cls.start_up_orig)
        cls.simulation_db = SQL(db_path=simulation_db_path,
                                schema_path=schema_path)
        cls.simulation_db.create_db()
        cls.simulation_db.create_table('clients')

        cls.outsider_db = SQL(db_path=cls.simulation_db.db_path,
                              schema_path=cls.simulation_db.schema_path)
        cls.outsider_db.access_db()

    @classmethod
    def tearDownClass(cls):
        cls.outsider_db.close()

        cls.simulation_db.close()
        cls.simulation_db.remove_db()

    def setUp(self):
        self.start_up_orig = MakeSimulationDbTests.start_up_orig
        self.simulation_db = MakeSimulationDbTests.simulation_db
        self.outsider_db = MakeSimulationDbTests.outsider_db

    @patch('os.path.exists', return_value=True)
    def test_collect_client_dbs(self, mock_exists):
        yaml_path = replace_atat_n('')
        simulation_db = MakeSimulationDbTests.simulation_db
        schema_parser, table_name, fixture = \
            inserts_fixture(simulation_db,
                            yaml_path,
                           'test_collect_client_dbs')
        expected = []
        for i in range(len(fixture)):
            expected.append(call(get_client_db_path(MakeSimulationDbTests.start_up_orig, i)))

        client_dbs = collect_client_dbs(simulation_db,
                                        MakeSimulationDbTests.start_up_orig)

        self.assertEqual(len(client_dbs), len(fixture))
        self.assertTrue(all([isinstance(client_db, SQL) for client_db in client_dbs]))
        mock_exists.assert_called()
        self.assertEqual(mock_exists.call_count, len(fixture))

       #print()
       #print('mock_exists.call_args_list =')
       #print(mock_exists.call_args_list)
       #print('expected =')
       #print(expected)
       #print()
       #print('mock_exists.method_calls =')
       #print(mock_exists.method_calls)
       #print('mock_exists.mock_calls =')
       #print(mock_exists.mock_calls)
        self.assertEqual(mock_exists.call_args_list, expected)

    def test_count_nodes(self):
        pass

    def test__select_client_db(self):
        pass

    def test_merge_client_dbs(self):
        pass

    def test_watson_make_simulation_db(self):
        pass

    def test_init_nodes_table(self):
        pass

    def test_init_nodes_table2(self):
        pass

if __name__ == '__main__':
    unittest.main()
