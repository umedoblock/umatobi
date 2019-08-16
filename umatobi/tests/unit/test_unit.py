import unittest
from test.support import run_unittest

from umatobi.tests.unit.test_lib import LibTests
from umatobi.tests.unit.test_sql import SQLTests

def test_main():
    # see: Lib/test/test_math.py
    unit_suite = unittest.TestSuite()
    unit_suite.addTest(unittest.makeSuite(LibTests))
    unit_suite.addTest(unittest.makeSuite(SQLTests))
    run_unittest(unit_suite)

# python3 -m unittest umatobi/tests/unit/test_unit.py
# __name__ = umatobi.tests.unit.test_unit
# python3 -m unittest umatobi.tests.unit.test_unit
# __name__ = umatobi.tests.unit.test_unit

# ... maybe no need test_main() ...
if __name__ == '__main__':
    test_main()
