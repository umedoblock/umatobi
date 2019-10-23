import os, sys, datetime, shutil
import unittest

from umatobi.tests import *
from umatobi.simulator.screen import Screen

class ScreenTests(unittest.TestCase):

    def test_screen_instance(self):
        screen = Screen(sys.argv)
        self.assertIsInstance(screen, Screen)

    def test___init__(self):
        pass

    def test__glut_init(self):
        pass

    def test_set_display(self):
        pass

    def test_start(self):
        pass

    def test__display(self):
        pass

    def test_display_main_thread(self):
        pass

    def test__print_fps(self):
        pass

    def test__simulation_info(self):
        pass

    def test__keyboard(self):
        pass

    def test_click_on_sample(self):
        pass

    def test_click_on(self):
        pass

    def test_idle(self):
        pass

class ManipulatingDBTests(unittest.TestCase):

    def test___init__(self):
        pass

    def test__init_maniplate_db(self):
        pass

    def test_run(self):
        pass

    def test_inhole_pickles_from_simlation_db(self):
        pass

    def test_completed_mission(self):
        pass

    def test_is_continue(self):
        pass

class LabelAreaTests(unittest.TestCase):

    def test___init__(self):
        pass

    def test_run(self):
        pass

    def test_update(self):
        pass

    def test_done(self):
        pass

class TrailerTests(unittest.TestCase):

    def test___init__(self):
        pass

    def test__glut_init(self):
        pass

    def test_start(self):
        pass

    def test__display(self):
        pass

    def test_print_fps(self):
        pass

    def test_simulation_info(self):
        pass

    def test_click_on_sample(self):
        pass

    def test_keyboard(self):
        pass

if __name__ == '__main__':
    unittest.main()
