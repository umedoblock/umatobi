import sys
import os
import pickle
import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lib.args import args_make_simulation_db
from lib import SCHEMA_PATH
import simulator.sql

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
                          select_columns='elapsed_time,pickle',
                          conditions='order by id')

def merge_client_dbs(client_dbs):
    records = []
    for client_db in client_dbs:
        _select_client_db(client_db)
        records.extend(client_db.queues)
    #158 records の sort をする時に、大量のmemoryが必要になると思われる。
    records.sort(key=lambda x: x['elapsed_time'])
  # for record in records:
  #     print(tuple(record))
    return records

def watson_make_simulation_db(simulation_db, watson_db):
    print('simulation_db =', simulation_db)
    print('watson_db =', watson_db)

    if os.path.exists(simulation_db.path):
        print('os.remove("{}")'.format(simulation_db.path))
        os.remove(simulation_db.path)
    simulation_db.create_db()
    simulation_db.create_table('simulation')
    simulation_db.create_table('growings')

    watson_db.access_db()

    watson_db.client_dbs = collect_client_dbs(watson_db)
  # watson_db.total_nodes = count_nodes(watson_db.client_dbs)
    watson_db.total_nodes = \
        watson_db.select('simulation', 'total_nodes')[0]['total_nodes']
    simulation_records = watson_db.select('simulation')
    L = []
    print('simulation_records =', simulation_records)
    print('simulation_records[0] =', simulation_records[0])
    print('simulation_records[0].keys() =', simulation_records[0].keys())
    print('tuple(simulation_records[0]) =', tuple(simulation_records[0]))
    print()
    L.append(tuple(simulation_records[0].keys()))
    L.append(tuple(simulation_records[0]))
    tups = tuple(L)
    print('tups =')
    print(tups)
    print()
    simulation_db.inserts('simulation', tups)
    simulation_db.commit()
  # print('dir(simulation_record) =', dir(simulation_record[0]))
  # print('simulation_record =', simulation_record[0].keys())
  # print('simulation_record =', tuple(simulation_record[0]))
    print('watson_db.total_nodes = {}'.format(watson_db.total_nodes))
    watson_db.records = merge_client_dbs(watson_db.client_dbs)
    growing = {}
    growing['id'] = None
    growing['elapsed_time'] = None
    growing['pickle'] = None
    keys = tuple(growing.keys())

    for i, key in enumerate(keys):
        if key == 'id':
            i_id = i
        elif key == 'elapsed_time':
            i_elapsed_time = i
        elif key == 'pickle':
            i_pickle = i

    growings = []
    growings.append(keys)

    # L[i_id] = None
    for record in watson_db.records:
        L = [None] * len(keys)
        L[i_elapsed_time] = record['elapsed_time']
        L[i_pickle] = record['pickle']
        growings.append(L)
    simulation_db.inserts('growings', growings)
    simulation_db.commit()

if __name__ == '__main__':
    args, simulation_db_path = args_make_simulation_db()
    if not simulation_db_path:
        raise RuntimeError('simulation_db_path is empty.')
    watson_db_path = simulation_db_path.replace(r'simulation.db', 'watson.db')

    simulation_db = simulator.sql.SQL(db_path=simulation_db_path,
                                      schema_path=SCHEMA_PATH)
    simulation_db.path = simulation_db_path
    watson_db = simulator.sql.SQL(db_path=watson_db_path)
    watson_db.simulation_db_path = simulation_db.path
    watson_db.path = watson_db_path

    watson_make_simulation_db(simulation_db, watson_db)

    for client_db in reversed(watson_db.client_dbs):
        client_db.close()
    watson_db.close()
    simulation_db.close()

  # print()
  # table_names = simulation_db.get_table_names()
  # print('table_names = {}'.format(table_names))
  # column_names = simulation_db.get_column_names('simulation')
  # print('column_names = {}'.format(column_names))
  # table_schema = simulation_db.get_table_schema('simulation')
  # print('table_schema = {}'.format(table_schema))
