import os, sys, datetime, shutil
import unittest

from umatobi.tests import *
from umatobi.simulator.screen import Screen

class ScreenTests(unittest.TestCase):
    def test_screen_instance(self):
        screen = Screen(sys.argv)
        self.assertIsInstance(screen, Screen)
