import unittest

from umatobi.lib import *

class MakeSimulationDbTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.start_up_orig = SimulationTime()

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
