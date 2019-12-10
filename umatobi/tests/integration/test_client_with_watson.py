# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import unittest
import shutil

from umatobi.tests import *
from umatobi.simulator.client import Client
from umatobi.simulator.watson import Watson
from umatobi.lib import *

class ClientStoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.simulation_time = SimulationTime()

    def setUp(self):
        watson_office_addr = ('localhost', 0)
        simulation_seconds = 30
        log_level = 'DEBUG'

        simulation_time = ClientStoryTests.simulation_time

        self.watson = Watson(watson_office_addr, simulation_seconds,
                             simulation_time, log_level)

    def tearDown(self):
        pass

    # client emurate client.start()
    # watson emurate watson.run()
    def test_client_story_with_watson(self):
      ######################################################################
      # The first half of simulation #######################################
      ######################################################################
        watson = self.watson
        num_nodes = 10

        watson.touch_simulation_db_on_clients()
        watson.open_office()

        # emulate client.start()
        client = Client(watson.watson_office_addr, num_nodes)

        client._consult_watson()

        client._has_a_lot_on_mind()

        client._confesses_darkness()

      ######################################################################
      # watson.relaxing() ##################################################
      # watson sleep until simulation time passed ##########################
      ######################################################################

      ######################################################################
      # The second half of simulation ######################################
      ######################################################################
        watson.release_clients()

        watson.watson_tcp_office.shutdown()
        watson._wait_client_db()

        client._waits_to_break_down()

#       # Client 終了処理開始。
        client._run_a_way()

        client._come_to_a_bad_end()

        client._thanks()

        # emulate client.start() done !

        watson.simulation_db.access_db()
        watson._merge_db_to_simulation_db()
        watson._create_simulation_table()
        watson._construct_simulation_table()
        watson.simulation_db.close()

        watson.watson_open_office.join()

if __name__ == '__main__':
    unittest.main()
