import os
import sys
import threading
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from simulator.watson import Watson
import p2p.core
import simulator.node

test_dir = os.path.dirname(__file__)

class TestWatson(unittest.TestCase):
    def test_watson_basic(self):
        office = ('localhost', 65530)
        simulation_seconds = 1
        simulation_dir = os.path.join(test_dir, 'umatobi-simulation')
        log_level = 'INFO'

        self.assertFalse(os.path.exists(watson_log))
        # watson for test
        watson = Watson(office, simulation_seconds, simulation_dir, log_level)

        self.assertTrue(os.path.exists(watson_log))

        watson.start()
        watson.join()

if __name__ == '__main__':
    unittest.main()
