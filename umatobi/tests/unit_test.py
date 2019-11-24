import unittest
from test.support import run_unittest

from umatobi.tests.unit.test_lib import LibTests, SimulationTimeTests
from umatobi.tests.unit.test_lib import SchemaParserTests
from umatobi.tests.unit.test_sql import SQLTests
from umatobi.tests.unit.test_core_node import CoreNodeTests
from umatobi.tests.unit.test_watson import WatsonTests
from umatobi.tests.unit.test_client import ClientTests
from umatobi.tests.unit.test_simulation import SimulationTests
from umatobi.tests.unit.test_theater import TheaterTests
from umatobi.tests.unit.test_screen import ScreenTests
from umatobi.tests.unit.test_node import NodeTests, NodeOfficeTests
from umatobi.tests.unit.test_darkness import DarknessTests

from umatobi.tests.unit.test_core_key import CoreKeyTests
from umatobi.tests.unit.test_logger import LoggerNodeTests, LoggerClientTests
from umatobi.tests.unit.test_mock_call_order import MockClientTests
from umatobi.tests.unit.test_fixture import FixtureTests

def test_main():
    # see: Lib/test/test_math.py
    unit_suite = unittest.TestSuite()

    unit_suite.addTest(unittest.makeSuite(LibTests))
    unit_suite.addTest(unittest.makeSuite(SimulationTimeTests))
    unit_suite.addTest(unittest.makeSuite(SchemaParserTests))
    unit_suite.addTest(unittest.makeSuite(SQLTests))
    unit_suite.addTest(unittest.makeSuite(CoreNodeTests))
    unit_suite.addTest(unittest.makeSuite(WatsonTests))
    unit_suite.addTest(unittest.makeSuite(ClientTests))
    unit_suite.addTest(unittest.makeSuite(SimulationTests))
    unit_suite.addTest(unittest.makeSuite(TheaterTests))
    unit_suite.addTest(unittest.makeSuite(ScreenTests))
    unit_suite.addTest(unittest.makeSuite(NodeTests))
    unit_suite.addTest(unittest.makeSuite(NodeOfficeTests))
    unit_suite.addTest(unittest.makeSuite(DarknessTests))
    unit_suite.addTest(unittest.makeSuite(FixtureTests))
    unit_suite.addTest(unittest.makeSuite(MakeSimulationDbTests))

    run_unittest(unit_suite)

# python3 -m unittest umatobi/tests/unit/test_unit.py
# __name__ = umatobi.tests.unit.test_unit
# python3 -m unittest umatobi.tests.unit.test_unit
# __name__ = umatobi.tests.unit.test_unit

if __name__ == '__main__':
    test_main()
