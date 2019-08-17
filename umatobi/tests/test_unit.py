import unittest
from test.support import run_unittest

from umatobi.tests.unit.test_lib import LibTests
from umatobi.tests.unit.test_sql import SQLTests
from umatobi.tests.unit.test_core_node import CoreNodeTests
from umatobi.tests.unit.test_watson import WatsonTests
from umatobi.tests.unit.test_client import ClientTests
from umatobi.tests.unit.test_simulation import SimulationTests
from umatobi.tests.unit.test_theater import TheaterTests
from umatobi.tests.unit.test_screen import ScreenTests
# failed
from umatobi.tests.unit.test_node import NodeTests, NodeOfficeTests
from umatobi.tests.unit.test_darkness import DarknessTests

def test_main():
    # see: Lib/test/test_math.py
    unit_suite = unittest.TestSuite()

    # success
    unit_suite.addTest(unittest.makeSuite(LibTests))
    unit_suite.addTest(unittest.makeSuite(SQLTests))
    unit_suite.addTest(unittest.makeSuite(CoreNodeTests))
    unit_suite.addTest(unittest.makeSuite(WatsonTests))
    unit_suite.addTest(unittest.makeSuite(ClientTests))
    unit_suite.addTest(unittest.makeSuite(SimulationTests))
    unit_suite.addTest(unittest.makeSuite(TheaterTests))
    unit_suite.addTest(unittest.makeSuite(ScreenTests))
    #failed
    unit_suite.addTest(unittest.makeSuite(NodeTests))
    unit_suite.addTest(unittest.makeSuite(NodeOfficeTests))
    unit_suite.addTest(unittest.makeSuite(DarknessTests))

    run_unittest(unit_suite)

# python3 -m unittest umatobi/tests/unit/test_unit.py
# __name__ = umatobi.tests.unit.test_unit
# python3 -m unittest umatobi.tests.unit.test_unit
# __name__ = umatobi.tests.unit.test_unit

# ... maybe no need test_main() ...
if __name__ == '__main__':
    test_main()
