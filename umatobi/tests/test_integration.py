import unittest
from test.support import run_unittest

from umatobi.tests.integration.test_client_with_watson import ClientStoryTests

from umatobi.tests.test_darkness import DarknessTests

def test_main():
    # see: Lib/test/test_math.py
    suite = unittest.TestSuite()
    # success

    # suite.addTests(tests)
    # failed
    suite.addTest(unittest.makeSuite(ClientStoryTests))

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
