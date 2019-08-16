import unittest
from test.support import run_unittest

from umatobi.tests.test_client import ClientTests
from umatobi.tests.test_watson import WatsonTests
from umatobi.tests.test_simulation import SimulationTests
from umatobi.tests.test_screen import ScreenTests
from umatobi.tests.test_theater import TheaterTests
from umatobi.tests.test_node import NodeTests, NodeOfficeTests
from umatobi.tests.test_darkness import DarknessTests

def test_main():
    # see: Lib/test/test_math.py
    suite = unittest.TestSuite()
    # suite.addTests(tests)
    suite.addTest(unittest.makeSuite(WatsonTests))
    suite.addTest(unittest.makeSuite(ClientTests))
    suite.addTest(unittest.makeSuite(SimulationTests))
    suite.addTest(unittest.makeSuite(ScreenTests))
    suite.addTest(unittest.makeSuite(TheaterTests))
    suite.addTest(unittest.makeSuite(NodeTests))
    suite.addTest(unittest.makeSuite(NodeOfficeTests))
    suite.addTest(unittest.makeSuite(DarknessTests))
    run_unittest(suite)

# >>> os.path
# <module 'posixpath' from
#'/Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7/posixpath.py'
# >

# https://docs.python.org/3/library/unittest.html
# @unittest.skip("demonstrating skipping")
# @unittest.skipIf(mylib.__version__ < (1, 3),
#                  "not supported in this library version")
# @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
# self.skipTest("...")
# with self.subTest(i=i):
#     self.assertEqual(i % 2, 0)

if __name__ == '__main__':
    test_main()
