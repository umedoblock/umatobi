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
    print('simulation_db =', simulation_db)
    if os.path.exists(simulation_db_path):
        print('os.remove("{}")'.format(simulation_db_path))
        os.remove(simulation_db_path)
    simulation_db.create_db()
    simulation_db.create_table('simulation')

    watson_db_path = simulation_db_path.replace(r'simulation.db', 'watson.db')
    watson_db = simulator.sql.SQL(db_path=watson_db_path)
    print('watson_db =', watson_db)
    watson_db.access_db()

    client_dbs = []
    total_nodes = 0
    client_rows = watson_db.select('clients', conditions='order by id')
    for client_row in client_rows:
        id_, num_nodes_ = (client_row[0], client_row[5])
        print('id={}, num_nodes_={}'.format(id_, num_nodes_))
      # print('id={}, num_nodes_={}'.format(type(id_), type(num_nodes_)))
        client_db_path = \
            simulation_db_path.replace(r'simulation.db',
                                        'client.{}.db'.format(id_))
        client_db = simulator.sql.SQL(db_path=client_db_path)
        client_db.id, client_db.num_nodes = id_, num_nodes_
        total_nodes += client_db.num_nodes
        print('client_db =', client_db)
        client_db.access_db()
        print('client_db.id =', client_db.id)
        client_dbs.append(client_db)
    print('total_nodes =', total_nodes)

  # print()
  # table_names = simulation_db.get_table_names()
  # print('table_names = {}'.format(table_names))
  # column_names = simulation_db.get_column_names('simulation')
  # print('column_names = {}'.format(column_names))
  # table_schema = simulation_db.get_table_schema('simulation')
  # print('table_schema = {}'.format(table_schema))
