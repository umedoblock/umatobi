import os, datetime
import sys, shutil
import threading
import unittest

from umatobi.test import *
from umatobi.simulator.watson import Watson, WatsonOffice
from umatobi.simulator.watson import WatsonOpenOffice, WatsonTCPOffice
from umatobi import lib

class WatsonTests(unittest.TestCase):
    SIMULATION_SECONDS = 30
    D_TIMEDELTA = {
        "test_watson_start": \
            datetime.timedelta(0, SIMULATION_SECONDS - 1, 0),
    }

    def setUp(self):
        self.watson_office_addr = ('localhost', 65530)
        simulation_dir = os.path.join(".", SIMULATION_DIR)
        self.log_level = 'INFO'
        self.start_up_orig = lib.make_start_up_orig()
        start_up_time = lib.y15sformat_time(self.start_up_orig)
        dir_name = os.path.join(simulation_dir, start_up_time)
        self.dir_name = dir_name

        td_zero = datetime.timedelta(0, 0, 0)
        td = self.D_TIMEDELTA.get(self._testMethodName, td_zero)
        self.watson = Watson(self.watson_office_addr, self.SIMULATION_SECONDS,
                        self.start_up_orig - td,
                        self.dir_name, self.log_level)

    def tearDown(self):
        # delete dbs, logs...
        shutil.rmtree(self.watson.dir_name, ignore_errors=True)

    def test_watson_basic(self):
        watson = self.watson

        expected_dir = os.path.join('.', SIMULATION_DIR, watson.start_up_time)
        expected_path = os.path.join('.', SIMULATION_DIR, watson.start_up_time, SIMULATION_DB)

        self.assertEqual(self.watson_office_addr, watson.watson_office_addr)
        self.assertEqual(expected_dir, watson.dir_name)
        self.assertEqual(expected_path, watson.simulation_db_path)
        self.assertEqual(0, watson.total_nodes)

    def test_watson_start(self):
        watson = self.watson
        # 以下では，watson.start() の emulate

        watson.touch_simulation_db_on_clients()
        watson_open_office = watson.open_office()

        watson.relaxing()

        watson.release_clients()
        watson.watson_tcp_office.shutdown()
        watson._wait_client_db()

        watson.simulation_db.access_db()
        watson._merge_db_to_simulation_db()
        watson._construct_simulation_table()
        watson.simulation_db.close()

if __name__ == '__main__':
    unittest.main()
