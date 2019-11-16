import os, re

from umatobi.constants import *
from umatobi import constants

TESTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)))
_UMATOBI_ROOT_PATH = \
    os.path.join(TESTS_PATH, 'umatobi-root')
_SIMULATION_ROOT_PATH = \
    os.path.join(TESTS_PATH, SIMULATION_DIR)

constants.SIMULATION_DIR_PATH = \
    re.sub(SIMULATION_ROOT_PATH, _SIMULATION_ROOT_PATH, SIMULATION_DIR_PATH)

constants.SIMULATION_SCHEMA_PATH = \
    os.path.join(constants.SIMULATION_DIR_PATH, SIMULATION_SCHEMA)

constants.UMATOBI_ROOT_PATH = _UMATOBI_ROOT_PATH
constants.SIMULATION_ROOT_PATH = _SIMULATION_ROOT_PATH

constants.LOGGER_STREAM = open(os.path.join(TESTS_PATH, 'stdout.log'), 'w')

ATAT_N = '@@N@@'

# tests original
TEST_SCHEMA = 'test.schema'
TEST_DB = 'test.db'
TEST_YAML = f'test{ATAT_N}.yaml'
YAML_DIR = 'yaml'
FIXTURES_DIR = 'fixtures'
FIXTURES_DIR_PATH = os.path.join(TESTS_PATH, FIXTURES_DIR)
YAML_DIR_PATH = os.path.join(TESTS_PATH, YAML_DIR)
TEST_SCHEMA_PATH = os.path.join(FIXTURES_DIR_PATH, TEST_SCHEMA)
TEST_DB_PATH = os.path.join(TESTS_PATH, TEST_DB)
TEST_SIMULATION_DB_PATH = os.path.join(TESTS_PATH, SIMULATION_DB)
TEST_YAML_PATH = os.path.join(YAML_DIR_PATH, TEST_YAML)
TEST_FIXTURES_PATH = os.path.join(FIXTURES_DIR_PATH, TEST_YAML)

RE_Y15S = r'20\d{2}-[01]\d{1}-[0123]\dT[012]\d[0-5]\d[0-5]\d'
RE_ISO8601 = r'20\d{2}-[01]\d{1}-[0123]\dT[012]\d:[0-5]\d:[0-5]\d\.\d{6}'
RE_CLIENT_N_DB = r'client\.\d+\.db$'

# transform constants for test
from umatobi.constants import *
