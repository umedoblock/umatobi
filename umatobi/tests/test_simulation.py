import os, sys, datetime, shutil
import unittest

from umatobi.test import *
from umatobi.simulation import get_host_port

class SimulationTests(unittest.TestCase):
    def test_get_host_port(self):
        host_port = "127.0.0.1:22222"
        self.assertEqual(("127.0.0.1", 22222), get_host_port(host_port))

if __name__ == '__main__':
    unittest.main()
