import os
import sys
import sqlite3

conns = []
for i in range(100000000):
    try:
        conn = sqlite3.connect('/tmp/sqlite3-open-max-{}.db'.format(i))
    except sqlite3.OperationalError as raiz:
        if raiz.args[0] == 'unable to open database file':
            print('max connections are {}.'.format(i - 1))
            for j in range(i):
                os.remove('/tmp/sqlite3-open-max-{}.db'.format(j))
            sys.exit(0)
        else:
            raise raiz

    conns.append(conn)
