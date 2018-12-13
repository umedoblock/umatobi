import os, sys, datetime, shutil
import unittest

from umatobi.test import *
from umatobi.simulator.screen import Screen

class TheaterTests(unittest.TestCase):
    def test_screen_instance(self):
        screen = Screen(sys.argv)
        self.assertIsInstance(screen, Screen)

if __name__ == '__main__':
    unittest.main()

