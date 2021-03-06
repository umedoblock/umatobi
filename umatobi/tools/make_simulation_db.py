import sys
import os
import pickle
import datetime
import sqlite3

from umatobi.log import *
from umatobi.constants import *
from umatobi.lib.args import args_make_simulation_db
from umatobi.simulator.sql import SQL

def collect_client_dbs(simulation_db):
    client_dbs = []
    client_rows = simulation_db.select('clients', conditions='order by id')
    for client_row in client_rows:
        id_, num_nodes_ = (client_row['id'], client_row['num_nodes'])
        logger.debug('id={}, num_nodes_={}'.format(id_, num_nodes_))
        simulation_db_dir = os.path.dirname(simulation_db.simulation_db_path)
        client_db_path = os.path.join(simulation_db_dir, f"client.{id_}.db")
        client_db = SQL(db_path=client_db_path)
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
        logger.info(f"len(client_db.queues)={len(client_db.queues)}")
        records.extend(client_db.queues)
    #158 records の sort をする時に、大量のmemoryが必要になると思われる。
    records.sort(key=lambda x: x['elapsed_time'])
    return records

def watson_make_simulation_db(simulation_db):
    logger.debug(f'simulation_db={simulation_db}')

    simulation_db.access_db()
    logger.info('create growings table.')
    try:
        simulation_db.create_table('growings')
    except sqlite3.OperationalError as err:
        if err.args == ('table growings already exists',):
            logger.debug('table growings already exists')
            simulation_db.drop_table('growings')
            simulation_db.create_table('growings')
        else:
            raise err

    simulation_db.client_dbs = collect_client_dbs(simulation_db)
    simulation_db.total_nodes = \
        simulation_db.select('simulation', 'total_nodes')[0]['total_nodes']

    logger.debug(f'simulation_db.total_nodes={simulation_db.total_nodes}')
    simulation_db.records = merge_client_dbs(simulation_db.client_dbs)
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
    for record in simulation_db.records:
        L = [None] * len(keys)
        L[i_elapsed_time] = record['elapsed_time']
        L[i_pickle] = record['pickle']
        growings.append(L)
    simulation_db.inserts('growings', tuple(growings))
    simulation_db.commit()

    for client_db in simulation_db.client_dbs:
        client_db.close()
    simulation_db.close()

# theater 内にて update() によって node を更新するので，
# 更新対象となる node の存在が不可欠である。
# その更新対象となるnode を dummy としてここで作成する。
# refs #14
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

# theater 内にて update() によって node を更新するので，
# 更新対象となる node の存在が不可欠である。
# その更新対象となるnode を dummy としてここで作成する。
# refs #14
def init_nodes_table2(db, total_nodes):
    db.init_table('nodes')
    logger.debug('created nodes table.')

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
    for i in range(total_nodes):
        db.insert('nodes', d_node)
    db.commit()

if __name__ == '__main__':
  # print(f"__file__ = {__file__}")
  # print(f"__name__ = {__name__}")
    args, simulation_db_path = args_make_simulation_db()
    if not simulation_db_path:
        raise RuntimeError('simulation_db_path is empty.')

    simulation_db = SQL(db_path=simulation_db_path,
                                      schema_path=SCHEMA_PATH)
    simulation_db.simulation_db_path = simulation_db_path

    watson_make_simulation_db(simulation_db)

  # print()
  # table_names = simulation_db.get_table_names()
  # print('table_names = {}'.format(table_names))
  # column_names = simulation_db.get_column_names('simulation')
  # print('column_names = {}'.format(column_names))
  # table_schema = simulation_db.get_table_schema('simulation')
  # print('table_schema = {}'.format(table_schema))
