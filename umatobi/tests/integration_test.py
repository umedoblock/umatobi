import unittest
from test.support import run_unittest

from umatobi.tests.constants import *

def test_main():
    integration_suite = unittest.TestSuite()

    test_loader = unittest.TestLoader()
    integration_tests = test_loader.discover(TESTS_INTEGRATION_PATH)
    integration_suite.addTests(integration_tests)
    run_unittest(integration_suite)

if __name__ == '__main__':
    test_main()
