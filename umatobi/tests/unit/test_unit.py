import unittest
from test.support import run_unittest

from umatobi.tests.unit.test_lib import LibTests

def test_main():
    # see: Lib/test/test_math.py
    unit_suite = unittest.TestSuite()
    unit_suite.addTests(unittest.makeSuite(LibTests))
    suite.addTest(unittest.makeSuite(LibTests))
    run_unittest(unit_suite)

# python3 -m unittest umatobi/tests/unit/test_unit.py
# __name__ = umatobi.tests.unit.test_unit
# python3 -m unittest umatobi.tests.unit.test_unit
# __name__ = umatobi.tests.unit.test_unit

# ... maybe no need test_main() ...
if __name__ == '__main__':
    test_main()
