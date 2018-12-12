import sqlite3
import pickle
import sys
import os

from umatobi.constants import *
from umatobi import simulator
from umatobi.lib.performance import log_now, stop_watch

def inserts_many_records(db, records):
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

    L = [None] * len(keys)
    # L[i_id] = None
    for record in records:
        L[i_elapsed_time] = record['elapsed_time']
        L[i_pickle] = record['pickle']
        growings.append(L)
    db.inserts('growings', growings)
    db.commit()

def insert_many_records(db, records):
    growing = {}
    growing['id'] = None
    for record in records:
        growing['elapsed_time'] = record['elapsed_time']
        growing['pickle'] = record['pickle']
        db.insert('growings', growing)
    db.commit()

def make_test_records(n_records):
    records = [None] * n_records
    d_sample = {
        'id': 1,
        'key': '0xe771f0cc12ebd75c2fe2555c9d5aa2d3',
        'status': 'active',
        'host': 'localhost',
        'port': 10001,
    }
    for i in range(n_records):
        d = {}
        d_sample['id'] = i + 1
        pickled = pickle.dumps(d_sample)
        d['id'] = None
        d['elapsed_time'] = log_now()
        d['pickle'] = pickled
        records[i] = d
    return records

def run():
    db_path = os.path.join(os.path.dirname(__file__), 'performance.db')
    if os.path.exists(db_path):
        os.remove(db_path)
        print('os.remove(db_path="{}")'.format(db_path))

    db = simulator.sql.SQL(db_path=db_path, schema_path=SCHEMA_PATH)
    print('db =', db)
    db.create_db()

    n_records = 1 * 200
    n_records = 10000 * 200
    n_records = 10000 * 2
    n_records = 10000 * 20
    print('n_records =', n_records)
    records = stop_watch(make_test_records, (n_records,),
                        'make_test_records()')
    args = (db, records)

    db.create_table('growings')
    stop_watch(inserts_many_records, args, 'inserts_many_records')
    os.remove(db_path)

    db_path2 = db_path + '.2'
    db2 = simulator.sql.SQL(db_path=db_path2, schema_path=SCHEMA_PATH)
    print('db2 =', db2)
    db2.create_db()
    db2.create_table('growings')
    args = (db2, records)
    stop_watch(insert_many_records, args, 'insert_many_records')
    os.remove(db_path2)

if __name__ == '__main__':
    run()
