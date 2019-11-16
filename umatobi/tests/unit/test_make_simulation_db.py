import unittest

import umatobi
from umatobi.tests import *
from umatobi.lib import *
from umatobi.simulator.sql import SQL

class MakeSimulationDbTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.start_up_orig = SimulationTime()

        cls.outsider_db = SQL(db_path=TEST_SIMULATION_DB_PATH,
                              schema_path=SIMULATION_SCHEMA_PATH)
       #cls.outsider_db.create_db()
       #cls.outsider_db.access_db()

    @classmethod
    def tearDownClass(cls):
        cls.outsider_db.close()
        cls.outsider_db.remove_db()

    def setUp(self):
        self.start_up_orig = MakeSimulationDbTests.start_up_orig

    def test_collect_client_dbs(self):
        pass

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
