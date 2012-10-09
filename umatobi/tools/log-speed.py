# 気になって気になってしょうがないので作成。
# 10 thread で 10000 件ずつ、計100000の書き込みをする。
# 書き込み先は それぞれ sqlite, logger。
# sqlite では :memory: と file に書き込みを行う。

import sqlite3
import os
import datetime
import threading

threads_num = 5
records_num = 10 * 10000

def stop_watch(func, message):
    s = datetime.datetime.today()
    func()
    e = datetime.datetime.today()
    t = (e - s).total_seconds()

    if True:
        print('{:>28s} の処理にかかった時間:'.format(message))
        print('{:.3f}'.format(t))
        print()
    else:
        print('{:>28s} の処理にかかった時間: {:.3f}'.format(message, t))

def log_now():
    now = datetime.datetime.today()
    return now.strftime('%Y%m%dT%H%M%S')

class SqliteLogger(threading.Thread):
    def __init__(self, no, cur, records_num, conn, filename):
        threading.Thread.__init__(self)
        print('filename =', filename)
        self.cur = cur
        self.conn = conn
        self.filename = filename
        self.no = no
        self.records_num = records_num

    def run(self):
        self.conn = sqlite3.connect(self.filename)
####### self.conn.isolation_level = 'BEGIN'
#       self.conn.isolation_level = 'IMMEDIATE' # 8.060
        self.conn.isolation_level = 'DEFERRED'  # 8.001, 7.995
#       self.conn.isolation_level = 'EXCLUSIVE' # 8.084
#       self.conn.isolation_level = None # unknown
#                                   default #     8.149
        print('conn.in_transaction 0 =', self.conn.in_transaction)
        self.cur = self.conn.cursor()
        sql = 'insert into logs values(?,?,?,?)'
        print('conn.in_transaction 1 =', self.conn.in_transaction)
        for i in range(self.records_num):
            now = log_now()
            tup = (None, now, 'info', 'message {:08x}'.format(i))
#           print('tup =', tup)
            self.cur.execute(sql, tup)
        print('conn.in_transaction 2 =', self.conn.in_transaction)
        self.conn.commit()
        print('conn.in_transaction 3 =', self.conn.in_transaction)
        self.cur.close()

def sqlite3_performance(filename):
    conn = sqlite3.connect(filename)
    cur = conn.cursor()
    records = [
        'id integer primary key autoincrement unique not null',
        'now text not null',
        'level text not null',
        'message text not null',
    ]
    cur.execute('create table logs ({})'.format(','.join(records)))

    conn.commit()
    cur.close()

    threads = []
    for i in range(threads_num):
        thread = SqliteLogger(i, cur, records_num, conn, filename)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

def sqlite3_memory_performance():
    sqlite3_performance(':memory:')

def sqlite3_file_performance():
    path = '/tmp/file.sqlite3.db'
    if os.path.exists(path):
        os.remove(path)
    sqlite3_performance(path)
  # os.remove(path)

# multi thread では :memory: を試せない。
# stop_watch(sqlite3_memory_performance, 'sqlite3_memory_performance()')
stop_watch(sqlite3_file_performance, 'sqlite3_file_performance()')
