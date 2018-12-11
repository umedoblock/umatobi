import os
import sys, shutil
import threading
import unittest

import umatobi.test
from umatobi import SIMULATION_DIR
from umatobi.simulator.watson import Watson
from umatobi import lib

class WatsonTests(unittest.TestCase):
    def setUp(self):
        self.watson_office_addr = ('localhost', 65530)
        self.simulation_seconds = 30
        simulation_dir = os.path.join(".", SIMULATION_DIR)
        self.log_level = 'INFO'
        self.start_up_orig = lib.make_start_up_orig()
        start_up_time = lib.y15sformat_time(self.start_up_orig)
        dir_name = os.path.join(simulation_dir, start_up_time)
        self.dir_name = dir_name

        self.watson = Watson(self.watson_office_addr, self.simulation_seconds,
                        self.start_up_orig,
                        self.dir_name, self.log_level)

    def tearDown(self):
        # delete dbs, logs...
        shutil.rmtree(self.watson.dir_name, ignore_errors=True)

    def test_watson_basic(self):
        watson = self.watson
        watson = Watson(self.watson_office_addr, self.simulation_seconds,
                        self.start_up_orig,
                        self.dir_name, self.log_level)

        expected_dir = os.path.join('.', SIMULATION_DIR, watson.start_up_time)
        expected_path = os.path.join('.', SIMULATION_DIR, watson.start_up_time, 'simulation.db')

        self.assertEqual(self.watson_office_addr, watson.watson_office_addr)
        self.assertEqual(expected_dir, watson.dir_name)
        self.assertEqual(expected_path, watson.simulation_db_path)
        self.assertEqual(0, watson.total_nodes)

if __name__ == '__main__':
    unittest.main()
