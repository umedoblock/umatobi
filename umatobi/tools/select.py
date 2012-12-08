import sys
import os
import sqlite3

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lib.args import args_db
import simulator.sql

if __name__ == '__main__':
    # examples:
    # umatobi/select.py --help
    # umatobi/select.py --show-timestamps
    # umatobi/select.py watson.db clients
    # umatobi/select.py --index=1 client.1.db pickles

    args, db_path = args_db('select.py')
  # print('args =', args)

    if db_path:
        print('db_path =', db_path)
        db = simulator.sql.SQL(db_path=db_path)
        db.set_logger(None, level='INFO')
        print('db =', db)
        db.access_db()
        print()
        table_names = db.get_table_names()
        table_name = args.table_name
        if not table_name in table_names:
            message = 'table name "{}" is not in table_names={}.'. \
                       format(table_name, table_names)
            raise RuntimeError(message)

        print('{} table'.format(table_name))
        rows = db.select(table_name)
        if rows:
            print(tuple(rows[0].keys()))
            for row in rows:
                print(tuple(row))
        else:
            print('no record.')

    _debug = False
    if _debug:
        sqls = ('select * from sqlite_master;', 'select * from pickles;')
        for sql in sqls:
            valid = sqlite3.complete_statement(sql)
            print('sql "{}" is {}'.format(sql, valid))
            if valid:
                rows = db.execute(sql)
                print('column_names =')
                print(db.get_column_names())
                print('rows =')
                for row in db.cur:
                    print(row)
                print('--')
            print()
