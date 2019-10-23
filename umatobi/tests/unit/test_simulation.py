import os, sys, datetime, shutil
import unittest

from umatobi.tests import *
from umatobi.lib import get_host_port

class SimulationTests(unittest.TestCase):

    def test_make_client(self):
        pass

    def test_args_(self):
        pass

    def test_get_host_port(self):
        host_port = "127.0.0.1:22222"
        self.assertEqual(("127.0.0.1", 22222), get_host_port(host_port))

    def test_not_found_simulation_conf(self):
        path = 'umatobi/umatobi/simulator/simulation.conf'

if __name__ == '__main__':
    unittest.main()
