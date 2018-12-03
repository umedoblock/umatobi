import sys
import os
import pickle
import datetime
import sqlite3

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lib.args import args_make_simulation_db
from lib import SCHEMA_PATH, make_logger
import simulator.sql

logger = make_logger(log_dir="", name=os.path.basename(__file__), level="DEBUG")

def collect_client_dbs(watson_db):
    client_dbs = []
    client_rows = watson_db.select('clients', conditions='order by id')
    for client_row in client_rows:
        id_, num_nodes_ = (client_row['id'], client_row['num_nodes'])
        logger.debug('id={}, num_nodes_={}'.format(id_, num_nodes_))
        client_db_path = \
            watson_db.simulation_db_path.replace(r'simulation.db',
                                        'client.{}.db'.format(id_))
        client_db = simulator.sql.SQL(db_path=client_db_path)
        client_db.id, client_db.num_nodes = id_, num_nodes_
        logger.debug(f'client_db={client_db}')
        client_db.access_db()
        logger.debug(f'client_db.id={client_db.id}')
        client_dbs.append(client_db)

    return client_dbs

def count_nodes(client_dbs):
    total_nodes = 0
    for client_db in client_dbs:
        total_nodes += client_db.num_nodes
    logger.debug(f'total_nodes={total_nodes}')
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
  #     logger.debug(f'tuple(record)')
    return records

def watson_make_simulation_db(simulation_db, watson_db):
    logger.debug(f'simulation_db={simulation_db}')
    logger.debug(f'watson_db={watson_db}')

    if os.path.exists(simulation_db.path):
        logger.debug(f'os.remove("{simulation_db.path}")')
        os.remove(simulation_db.path)
    simulation_db.create_db()
    simulation_db.create_table('simulation')
    simulation_db.create_table('growings')
    simulation_db.create_table('nodes')

    watson_db.access_db()

    watson_db.client_dbs = collect_client_dbs(watson_db)
  # watson_db.total_nodes = count_nodes(watson_db.client_dbs)
    watson_db.total_nodes = \
        watson_db.select('simulation', 'total_nodes')[0]['total_nodes']

    logger.debug(f'watson_db.total_nodes={watson_db.total_nodes}')
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

    simulation_db.take_table(watson_db, 'simulation')
    init_nodes_table(simulation_db)

def init_nodes_table(simulation_db):
    simulation_db.init_table('nodes')
    logger.debug('created nodes table.')

    simulation_db.total_nodes = \
        simulation_db.select_one('simulation', 'total_nodes')
    logger.debug(f'simulation_db.total_nodes={simulation_db.total_nodes}')
    d_node = {
        'id': None,
        'host': 'dummy host',
        'port': 0,
        'keyID': 0x00000000,
        'key': b'0x dummy',
        'rad': 0.0,
        'x': 0.0,
        'y': 0.0,
        'status': 'dummy status',
    }
    for i in range(simulation_db.total_nodes):
        simulation_db.insert('nodes', d_node)
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
