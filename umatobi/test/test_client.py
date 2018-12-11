import os
import sys, shutil
import unittest

from umatobi.simulator.client import Client
from umatobi.simulator.watson import Watson
from umatobi import lib
from umatobi.simulator import watson

class ClientTests(unittest.TestCase):
    def setUp(self):
        watson_office_addr = ('localhost', 65530)
        simulation_seconds = 20
        simulation_dir = "."
        log_level = 'INFO'

        start_up_orig = lib.make_start_up_orig()
        start_up_time = lib.y15sformat_time(start_up_orig)

        dir_name = os.path.join(simulation_dir, start_up_time)

        if not os.path.isdir(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        self.watson = Watson(watson_office_addr, simulation_seconds,
                        start_up_orig,
                        dir_name, log_level)

    def tearDown(self):
        # delete dbs, logs...
        shutil.rmtree(self.watson.dir_name, ignore_errors=True)

    def test_client_basic(self):
        watson_office_addr = ('localhost', 65530)
        num_nodes = 10

        client = Client(watson_office_addr, num_nodes)

        self.assertEqual(watson_office_addr, client.watson_office_addr)
        self.assertEqual(num_nodes, client.num_nodes)

if __name__ == '__main__':
    unittest.main()
