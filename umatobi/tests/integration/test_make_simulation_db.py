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
        cls.path_maker = PathMaker(SimulationTime())
        cls.path_maker.set_simulation_schema()

        simulation_db_path = cls.path_maker.get_simulation_db_path()
        schema_path = cls.path_maker.get_simulation_schema_path()
        cls.simulation_db = SQL(db_path=simulation_db_path,
                                schema_path=schema_path)
        cls.simulation_db.create_db()

        cls.outsider_db = SQL(db_path=cls.simulation_db.db_path,
                              schema_path=cls.simulation_db.schema_path)
        cls.outsider_db.access_db()

    @classmethod
    def tearDownClass(cls):
        cls.outsider_db.close()

        cls.simulation_db.close()
        cls.simulation_db.remove_db()

    def setUp(self):
        self.simulation_db = MakeSimulationDbTests.simulation_db
        self.simulation_db.create_table('clients')
        self.outsider_db = MakeSimulationDbTests.outsider_db

    def tearDown(self):
        for table_name in self.simulation_db.get_table_names():
            self.simulation_db.drop_table(table_name)

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
            expected.append(call(self.path_maker.get_client_db_path(i)))

        client_dbs = collect_client_dbs(simulation_db, self.path_maker)

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

        for i, client_db in enumerate(client_dbs):
            client_db.remove_db()

    def test_count_nodes(self):
        pass

    def test__select_client_db(self):
        pass

    @patch('os.path.exists', return_value=True)
    def test_merge_client_dbs(self, mock_exists):
        yaml_path = replace_atat_n('')
        simulation_db = MakeSimulationDbTests.simulation_db
        schema_parser, table_name, fixture = \
            inserts_fixture(simulation_db,
                            yaml_path,
                           'test_merge_client_dbs')

        client_dbs = collect_client_dbs(simulation_db, self.path_maker)
        mock_exists.assert_called()
        self.assertEqual(mock_exists.call_count, len(fixture))

        for client_db in client_dbs:
            client_db.create_table('growings')

        growing_dicts = [None] * len(client_dbs)
        for i, client_db in enumerate(client_dbs):
            growing_dicts[i] = make_growing_dicts(client_db.num_nodes,
                                                  120,
                                                  client_db.node_index)
            gds = growing_dicts[i]
            self.assertTrue(any((gds[j]['elapsed_time'] < gds[j+1]['elapsed_time']) for j in range(len(gds))))
            self.assertEqual(growing_dicts[i][0]['elapsed_time'],
                             growing_dicts[i][1]['elapsed_time'])
            client_db.inserts_via_dict('growings', growing_dicts[i])
            client_db.commit()

        sorted_records = merge_client_dbs(client_dbs)

        self.assertEqual(len(sorted_records), 120 * 2)
        for i, sorted_record in enumerate(sorted_records[:-2]):
            self.assertLessEqual(sorted_records[i]['elapsed_time'],
                                 sorted_records[i+1]['elapsed_time'])

        for i, client_db in enumerate(client_dbs):
            client_db.remove_db()

    def test_watson_make_simulation_db(self):
        pass

    def test_init_nodes_table(self):
        pass

    def test_init_nodes_table2(self):
        pass

if __name__ == '__main__':
    unittest.main()
