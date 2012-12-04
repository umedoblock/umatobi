import sys
import os
import pickle
import datetime

from xxx import args_xxx, get_xxx_path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import simulator.sql

def args_timestamp():
    parser = args_xxx(description='make_simulation_db.py')
    args = parser.parse_args()
    args.xxx_file = 'simulation.db'
    return args

def collect_client_dbs(watson_db):
    client_dbs = []
    client_rows = watson_db.select('clients', conditions='order by id')
    for client_row in client_rows:
        id_, num_nodes_ = (client_row['id'], client_row['num_nodes'])
        print('id={}, num_nodes_={}'.format(id_, num_nodes_))
        client_db_path = \
            watson_db.simulation_db_path.replace(r'simulation.db',
                                        'client.{}.db'.format(id_))
        client_db = simulator.sql.SQL(db_path=client_db_path)
        client_db.id, client_db.num_nodes = id_, num_nodes_
        print('client_db =', client_db)
        client_db.access_db()
        print('client_db.id =', client_db.id)
        client_dbs.append(client_db)

    return client_dbs

def count_nodes(client_dbs):
    total_nodes = 0
    for client_db in client_dbs:
        total_nodes += client_db.num_nodes
    print('total_nodes =', total_nodes)
    return total_nodes

def _select_client_db(client_db):
    client_db.queues = \
        client_db.select('growings',
                          select_columns='moment,pickle',
                          conditions='order by id')
    client_db.queues = tuple(client_db.queues)

def merge_client_dbs(client_dbs):
    records = []
    for client_db in client_dbs:
        _select_client_db(client_db)
        records.extend(client_db.queues)
    #158 records の sort をする時に、大量のmemoryが必要になると思われる。
    records.sort(key=lambda x: x['moment'])
  # for record in records:
  #     print(record)
    return records

def clients_db_grow_up_to_simulation_db(simulation_db, records):
    growing = {}
    growing['id'] = None
    for record in records:
        growing['moment'] = record['moment']
        growing['pickle'] = record['pickle']
        simulation_db.insert('growings', growing)
    simulation_db.commit()

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
    simulation_db.create_table('growings')

    watson_db_path = simulation_db_path.replace(r'simulation.db', 'watson.db')
    watson_db = simulator.sql.SQL(db_path=watson_db_path)
    watson_db.simulation_db_path = simulation_db_path
    print('watson_db =', watson_db)
    watson_db.access_db()

    watson_db.client_dbs = collect_client_dbs(watson_db)
    watson_db.total_nodes = count_nodes(watson_db.client_dbs)
    watson_db.records = merge_client_dbs(watson_db.client_dbs)
    clients_db_grow_up_to_simulation_db(simulation_db, watson_db.records)
    simulation_db.close()

  # print()
  # table_names = simulation_db.get_table_names()
  # print('table_names = {}'.format(table_names))
  # column_names = simulation_db.get_column_names('simulation')
  # print('column_names = {}'.format(column_names))
  # table_schema = simulation_db.get_table_schema('simulation')
  # print('table_schema = {}'.format(table_schema))
