import os, sys

# for package
SIMULATOR_DIR = 'simulator'

# for simulation
SIMULATION_DIR = 'umatobi-simulation'
SIMULATION_DB = 'simulation.db'
SIMULATION_SCHEMA = 'simulation.schema'
WATSON_DB = 'watson.db'
MASTER_PALM = 'master_palm.txt'

UMATOBI_ROOT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)))
SIMULATION_ROOT_PATH = os.path.join(os.path.expanduser('~'), SIMULATION_DIR)

# ROOT_DIR_PATH/umatobi-simulation/20190919T211132/simulation.schema
#                                                 /simulation.db
#                                                 /watson.db
#                                                 /client.1.db
#                                                 /master_palm.txt

# abspath suffix is "_PATH"
SIMULATION_TIME_ATAT = '@@SIMULATION_TIME@@'
SIMULATION_DIR_PATH = os.path.join(SIMULATION_ROOT_PATH, SIMULATION_TIME_ATAT)
SIMULATION_SCHEMA_PATH = os.path.join(UMATOBI_ROOT_PATH, SIMULATOR_DIR, SIMULATION_SCHEMA)
SIMULATION_SCHEMA_ORIG = os.path.join(UMATOBI_ROOT_PATH, SIMULATOR_DIR, SIMULATION_SCHEMA)

#   %(relativeCreated)d Time in ms when the LogRecord was created,
LOGGER_FMT = '%(relativeCreated)d %(name)s %(levelname)s %(filename)s %(funcName)s() - %(message)s'
LOGGER_SUFFIX = f" - process_id=%(process)d therad_id=%(thread)d"
LOGGER_STREAM = sys.stdout
