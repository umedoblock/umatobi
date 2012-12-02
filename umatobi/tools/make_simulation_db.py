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
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'simulator',
                              'simulation_tables.schema')
    simulation_db = simulator.sql.SQL(db_path=simulation_db_path,
                                      schema_path=schema_path)
    print('schema_path =', schema_path)
    print('simulation_db_path =', simulation_db_path)
    if os.path.exists(simulation_db_path):
        print('os.remove("{}")'.format(simulation_db_path))
        os.remove(simulation_db_path)
    simulation_db.create_db()
    simulation_db.create_table('simulation')

    table_names = simulation_db.get_table_names()
    print('table_names = {}'.format(table_names))
    column_names = simulation_db.get_column_names('simulation')
    print('column_names = {}'.format(column_names))
    table_schema = simulation_db.get_table_schema('simulation')
    print('table_schema = {}'.format(table_schema))
