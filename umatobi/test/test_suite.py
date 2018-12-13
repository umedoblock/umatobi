import unittest
from test.support import run_unittest

from umatobi.test.test_lib import LibTests
from umatobi.test.test_client import ClientTests
from umatobi.test.test_watson import WatsonTests
from umatobi.test.test_sql import SQLTests
from umatobi.test.test_simulation import SimulationTests
from umatobi.test.test_screen import ScreenTests
from umatobi.test.test_theater import TheaterTests

def test_main():
    # see: Lib/test/test_math.py
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LibTests))
    suite.addTest(LibTests('test_y15sformat_time')) # OK
    suite.addTest(unittest.makeSuite(WatsonTests))
    suite.addTest(unittest.makeSuite(ClientTests))
    suite.addTest(unittest.makeSuite(SQLTests))
    suite.addTest(unittest.makeSuite(SimulationTests))
    suite.addTest(unittest.makeSuite(ScreenTests))
    suite.addTest(unittest.makeSuite(TheaterTests))
    run_unittest(suite)

if __name__ == '__main__':
    test_main()
