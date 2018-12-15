import os

SIMULATION_DIR = 'umatobi-simulation'
SIMULATION_DB = 'simulation.db'
SIMULATION_SCHEMA = 'simulation.schema'
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'simulator', SIMULATION_SCHEMA)
MASTER_HAND = 'master_hand.txt'
WATSON_DB = 'watson.db'
