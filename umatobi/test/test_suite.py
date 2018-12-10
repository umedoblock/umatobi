import unittest
from test.support import run_unittest

from umatobi.test.test_lib import LibTests

# from umatobi.test import test_client
# from umatobi.test import test_watson

def test_main():
    # see: Lib/test/test_math.py
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LibTests))
    suite.addTest(LibTests('test_y15sformat_time')) # OK
 #  suite.addTest(unittest.MakeSuite(test_watson.WatsonTests))
 #  suite.addTest(unittest.MakeSuite(test_client.ClientTests))
    run_unittest(suite)

if __name__ == '__main__':
    test_main()
