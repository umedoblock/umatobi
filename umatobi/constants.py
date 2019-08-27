import os, sys

SIMULATION_DIR = 'umatobi-simulation'
SIMULATION_DB = 'simulation.db'
SIMULATION_SCHEMA = 'simulation.schema'
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'simulator', SIMULATION_SCHEMA)
MASTER_HAND = 'master_hand.txt'
WATSON_DB = 'watson.db'

#   %(relativeCreated)d Time in ms when the LogRecord was created,
LOGGER_FMT = '%(relativeCreated)d %(name)s %(levelname)s %(filename)s %(funcName)s() - %(message)s'
LOGGER_SUFFIX = f" - process_id=%(process)d therad_id=%(thread)d"
LOGGER_STREAM = sys.stdout
