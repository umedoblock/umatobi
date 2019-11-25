# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import os, sys, datetime, shutil
import unittest

from umatobi.tests import *
from umatobi.tools.theater import are_there_any_seats

class TheaterTests(unittest.TestCase):
    def test_are_there_any_seats(self):
        self.assertEqual("available", are_there_any_seats())

if __name__ == '__main__':
    unittest.main()
