import unittest
from test.support import run_unittest

from umatobi.test.test_lib import LibTests
from umatobi.test.test_client import ClientTests
from umatobi.test.test_watson import WatsonTests

def test_main():
    # see: Lib/test/test_math.py
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LibTests))
    suite.addTest(LibTests('test_y15sformat_time')) # OK
    suite.addTest(unittest.makeSuite(WatsonTests))
    suite.addTest(unittest.makeSuite(ClientTests))
    run_unittest(suite)

if __name__ == '__main__':
    test_main()
