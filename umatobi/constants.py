# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import os, sys

# abspath suffix is "_PATH"
# dirname suffix is "_DIR"

# for package
SIMULATOR_DIR = 'simulator'

# must replace to appropriate value
ATAT_SIMULATION_TIME = '@@SIMULATION_TIME@@'
ATAT_N = '@@N@@'

# for simulation
SIMULATION_DIR = 'umatobi-simulation'
SIMULATION_DB = 'simulation.db'
SIMULATION_SCHEMA = 'simulation.schema'
WATSON_DB = 'watson.db'
MASTER_PALM = 'master_palm.txt'
CLIENT_N_DB = f'client.{ATAT_N}.db'

# These paths are relative to UMATOBI_ROOT_PATH..
UMATOBI_ROOT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)))
SIMULATION_SCHEMA_PATH = os.path.join(UMATOBI_ROOT_PATH, SIMULATOR_DIR, SIMULATION_SCHEMA)

# These paths are relative to SIMULATOR_DIR.
SIMULATION_ROOT_PATH = os.path.join(os.path.expanduser('~'), SIMULATION_DIR)
SIMULATION_DIR_PATH = os.path.join(SIMULATION_ROOT_PATH, ATAT_SIMULATION_TIME)

# ROOT_DIR_PATH/umatobi-simulation/20190919T211132/simulation.schema
#                                                 /simulation.db
#                                                 /watson.db
#                                                 /client.1.db
#                                                 /master_palm.txt

#   %(relativeCreated)d Time in ms when the LogRecord was created,
LOGGER_FMT = '%(relativeCreated)d %(name)s %(levelname)s %(filename)s %(funcName)s() - %(message)s'
LOGGER_SUFFIX = f" - process_id=%(process)d thread_id=%(thread)d"
LOGGER_STREAM = sys.stdout
