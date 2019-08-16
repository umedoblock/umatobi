import re, os, io
import sys, shutil
import unittest

from umatobi.tests import *
from umatobi.simulator.client import Client
from umatobi.simulator.watson import Watson
from umatobi import lib
from umatobi.simulator import watson

class ClientTests(unittest.TestCase):
    def setUp(self):
        watson_office_addr = ('localhost', 0)
        simulation_seconds = 3
        simulation_dir = SIMULATION_DIR
        log_level = 'DEBUG'

        start_up_orig = lib.make_start_up_orig()
        start_up_time = lib.y15sformat_time(start_up_orig)

        dir_name = os.path.join(simulation_dir, start_up_time)

        if not os.path.isdir(dir_name):
            print(f"os.makedirs(dir_name={dir_name}, exist_ok=True)")
            os.makedirs(dir_name, exist_ok=True)

        self.watson = Watson(watson_office_addr, simulation_seconds,
                        start_up_orig,
                        dir_name, log_level)

    def tearDown(self):
        # delete dbs, logs...
        shutil.rmtree(self.watson.dir_name, ignore_errors=True)

    def test_client_break_down(self):
        watson_office_addr = ('localhost', 0)
        num_nodes = 10

        client = Client(watson_office_addr, num_nodes)

        client._tcp_sock = MockIO(b'break down.')
        with self.assertLogs('umatobi', level='INFO') as cm:
            client._wait_break_down()
        self.assertRegex(cm.output[0], r'^INFO:umatobi:.*\._wait_break_down\(\)')
        self.assertRegex(cm.output[1], r'^INFO:umatobi:.*\._wait_break_down\(\), .* got break down from \.*')


    def test_client_basic(self):
        watson_office_addr = ('localhost', 0)
        num_nodes = 10

        client = Client(watson_office_addr, num_nodes)

        self.assertEqual(watson_office_addr, client.watson_office_addr)
        self.assertEqual(num_nodes, client.num_nodes)

    def test_client_story_with_watson(self):
        watson = self.watson
        num_nodes = 10

        watson.touch_simulation_db_on_clients()
        watson.open_office()

        # emulate client.start()
        client = Client(watson.watson_office_addr, num_nodes)
        client.consult_watson()

        client._make_growings_table()

        client._start_darkness()

        watson.release_clients()
        watson.watson_tcp_office.shutdown()
        client._wait_break_down()

#       # Client 終了処理開始。
        client._release()

        client.close()
        # emulate client.start() done !

        watson.watson_open_office.join()

if __name__ == '__main__':
    unittest.main()
