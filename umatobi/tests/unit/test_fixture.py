import unittest
import sys

from umatobi.tests import *
from umatobi.lib import *

pa = TEST_YAML_PATH.replace(ATAT_N, '1')
class FixtureTests(unittest.TestCase):

    yaml_path = 'tests/fixtures/test.yaml'
  # @fixtures(yaml_path, 'quentin')
  # @fixtures(yaml_path, 'quentin')
    @fixtures(yaml_path, 'quentin')
    def test_fixture(self):
        print(f'self = {self}', file=sys.stderr)
#       print('fixture_yaml1 =', fixture_yaml1)
#       self.assertEqual(fixture_yaml1, 1)

if __name__ == '__main__':
    unittest.main()
