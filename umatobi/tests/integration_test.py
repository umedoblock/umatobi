# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import unittest
from test.support import run_unittest

from umatobi.tests.constants import *

def test_main():
    integration_suite = unittest.TestSuite()

    test_loader = unittest.TestLoader()
    integration_tests = test_loader.discover(TESTS_INTEGRATION_DIR)
    integration_suite.addTests(integration_tests)
    run_unittest(integration_suite)

if __name__ == '__main__':
    test_main()
