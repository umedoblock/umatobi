# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import os
import sys
import sqlite3

conns = []
connfmt = '/tmp/sqlite3-open-max-{}.db'
for i in range(100000000):
    try:
        conn = sqlite3.connect(connfmt.format(i))
    except sqlite3.OperationalError as raiz:
#       print('raiz =', raiz)
#       print('raiz.args =', raiz.args)
        if raiz.args == ('unable to open database file',):
            break
        else:
            raise raiz

    conns.append(conn)
#   if len(conns) > 1010:
#       break

print('sqlite3.connect() max connections are {}.'.format(len(conns)))

fs = []
ffmt = '/tmp/file-open-max-{}.bin'
for i in range(100000000):
    try:
        f = open(ffmt.format(i), 'wb')
    except IOError as raiz:
#       print('raiz =', raiz)
#       print('raiz.args =', raiz.args)
        if raiz.args == (24, 'Too many open files'):
            break
        else:
            raise raiz

    fs.append(f)

print('open() max are {}.'.format(len(fs)))

for i, conn in enumerate(conns):
    conn.close()
    os.remove(connfmt.format(i))

for i, f in enumerate(fs):
    f.close()
    os.remove(ffmt.format(i))

print('sqlite3.conn() max plus open() max are {}.'.
    format(len(conns) + len(fs)))
