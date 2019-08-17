import os

SIMULATION_DIR = 'umatobi-simulation'
SIMULATION_DB = 'simulation.db'
SIMULATION_SCHEMA = 'simulation.schema'
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'simulator', SIMULATION_SCHEMA)
MASTER_HAND = 'master_hand.txt'
WATSON_DB = 'watson.db'

CONSTRAINED_NODE = set([
            'host', 'port', 'id', 'start_up_time',
            'byebye_nodes', '_queue_darkness'
        ])

KEY_BITS = 256
KEY_OCTETS = KEY_BITS // 8
# KEY_BYTES = KEY_OCTETS
