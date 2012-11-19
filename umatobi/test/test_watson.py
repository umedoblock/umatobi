import os
import sys
import threading
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from simulator.watson import Watson
from lib import get_start_up
import p2p.core
import simulator.node

test_dir = os.path.dirname(__file__)

class TestWatson(unittest.TestCase):
    def test_watson_basic(self):
        office = ('localhost', 65530)
        simulation_seconds = 1
        simulation_dir = os.path.join(test_dir, 'umatobi-simulation')
        start_up = get_start_up()

        db_dir = os.path.join(simulation_dir, start_up)
        watson_log = os.path.join(db_dir, 'watson.log')

        # watsonが書き出す log 用の directory 作成
        os.makedirs(db_dir)

        self.assertFalse(os.path.exists(watson_log))
        # watson for test
        watson = Watson(office, simulation_seconds,
                        simulation_dir, start_up)

        self.assertTrue(os.path.exists(watson_log))

        watson.start()
        watson.join()

if __name__ == '__main__':
    unittest.main()
