import sys
import os
import sqlite3

from xxx import args_xxx, get_xxx_path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import simulator.sql

def args_db():
    parser = args_xxx(description='select.py')
    parser.add_argument(# db file
                        metavar='db file', dest='xxx_file',
                        nargs='?', default='',
                        help='simulation.db, watson.db, or client.1.db, ...')
    parser.add_argument(# table name
                        metavar='table name', dest='table_name',
                        nargs='?', default='',
                        help='table name')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    # examples:
    # umatobi/select.py --help
    # umatobi/select.py --show-timestamps
    # umatobi/select.py watson.db clients
    # umatobi/select.py --index=1 client.1.db pickles

    args = args_db()
  # print('args =', args)
    db_path = get_xxx_path(args, 'db')

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
        print('rows =', rows)
        if rows:
            print(rows[0].keys())
        for row in rows:
            print(tuple(row))

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
