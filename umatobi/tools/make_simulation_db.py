import sys
import os

from xxx import args_xxx, get_xxx_path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import simulator.sql

def args_timestamp():
    parser = args_xxx(description='make_simulation_db.py')
    args = parser.parse_args()
    args.xxx_file = 'simulation.db'
    return args

if __name__ == '__main__':
    args = args_timestamp()
    simulation_db_path = get_xxx_path(args, 'db')
    simulation_db = simulator.sql.SQL(db_path=simulation_db_path)
    print('simulation_db_path =', simulation_db_path)
