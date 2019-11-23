import unittest

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

#   def test_collect_client_dbs(self):
#       client_dbs = collect_client_dbs(self.simulation_db)

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
