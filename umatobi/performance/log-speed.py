# 気になって気になってしょうがないので作成。
# 10 thread で 10000 件ずつ、計100000の書き込みをする。
# 書き込み先は それぞれ sqlite, logger。
# sqlite では :memory: と file に書き込みを行う。
# #102 にまとめておいた。

# 5 thread 100,000 件で試してみた。
# 結果としては、
# sqlite3 20秒前後
#  logger 70秒弱
# 圧倒的な早さでsqlite3が勝った。

import sqlite3
import os
import sys
import threading
import logging

from umatobi.lib.performance import stop_watch
from umatobi.lib.performance import log_now

threads_num = 1
records_num = 1
threads_num = 5
records_num = 10 * 10000

FORMAT = '%(asctime)-15s %(now)s %(level)-5s %(log_message)s %(message)s'
logging.basicConfig(format=FORMAT, filename='/tmp/loggerlogger.log', level=logging.INFO)
d = { 'clientip' : '192.168.0.1', 'user' : 'fbloggs' }
logger = logging.getLogger('loggerlogger')
# logger.warning('Protocol problem: %s', 'connection reset', extra=d)

class LoggerLogger(threading.Thread):
    def __init__(self, id, records_num, lock=None):
        threading.Thread.__init__(self)
      # print('LoggerLogger() filename =', dir(logging))
        self.id = id
        self.records_num = records_num
        self.lock = lock

    def run(self):
        # 排他処理開始
        if self.lock:
            self.lock.acquire()

        sql = 'insert into logs values(?,?,?,?)'
      # くっそ遅い
      # もしも計測方法に誤りがなければ、sqlite3で決まり。
      # logger_performance() の処理にかかった時間:
      # 72.178
      # logger_performance() の処理にかかった時間:
      # d={} を for の外に出したけど、それでも遅い。
      # 多分、FORMAT の解析とか作成とかそんなものに時間を取られているんだろう。
      # 55.828
      # こりゃあ、文句なしで sqlite3 を採用だ。

        for i in range(self.records_num):
            now = log_now()
            d = {'id': None, 'now': now, 'level': 'info', 'log_message': 'message {:08x}'.format(i)}
          # print('d =', d)
            logger.info('abc', extra=d)

        # 排他処理終了
        if self.lock:
            self.lock.release()

class SqliteLogger(threading.Thread):
    def __init__(self, id, cur, records_num, conn, filename):
        threading.Thread.__init__(self)
        print('filename =', filename)
        self.cur = cur
        self.conn = conn
        self.filename = filename
        self.id = id
        self.records_num = records_num

    def run(self):
        self.conn = sqlite3.connect(self.filename)
####### self.conn.isolation_level = 'BEGIN'
        self.conn.isolation_level = 'IMMEDIATE' # 8.060
                                                # 20.508
                                                # 20.483
                                                # 20.279
                                                # 20.042
                                                # 20.198
#       self.conn.isolation_level = 'DEFERRED'  # 8.001, 7.995, 200 * 1000
                                                # 20.520,       500 * 1000
#       self.conn.isolation_level = 'EXCLUSIVE' # 8.084
                                                # 23.284
#       self.conn.isolation_level = None # unknown
#                                   default #     8.149
                                                # 20.399
        print('conn.in_transaction 0 =', self.conn.in_transaction)
        self.cur = self.conn.cursor()
        table_name = "logs"
        print('conn.in_transaction 1 =', self.conn.in_transaction)
        d = {}
        for i in range(self.records_num):
            d.clear()
            d['id'] = None
            d['now'] = log_now()
            d['level'] = 'info'
            d['message'] = 'message {:08x}'.format(i)

            sql = construct_sql_by_dict(table_name, d)
            while True:
                try:
                    self.cur.execute(sql, tuple(d.values()))
                except sqlite3.OperationalError as raiz:
                    if raiz.args[0] == 'database is locked':
                        continue
                    else:
                        raise raiz
                break
        print('conn.in_transaction 2 =', self.conn.in_transaction)
        self.conn.commit()
        print('conn.in_transaction 3 =', self.conn.in_transaction)
        self.cur.close()

def construct_sql_by_dict(table_name, d):
    sql = ""
    _key_names = ("', '".join(['{}'] * len(d))).format(*d.keys())
    part_keys = f"('{_key_names}')"

    hatenas = '({})'.format(', '.join('?' * len(d)))
    sql = "insert into " + table_name + part_keys + " values" + hatenas
    return sql

def logger_performance():
    path = '/tmp/loggerlogger.log'
    if os.path.exists(path):
        os.remove(path)
    threads = []
    for i in range(threads_num):
        thread = LoggerLogger(i, records_num)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

def logger_performance_sequential():
    path = '/tmp/loggerlogger.log'
    if os.path.exists(path):
        os.remove(path)
    threads = []
    lock = threading.Lock()
    for i in range(threads_num):
        thread = LoggerLogger(i, records_num, lock=lock)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

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

import cProfile
# multi thread では :memory: を試せない。
# stop_watch(sqlite3_memory_performance, 'sqlite3_memory_performance()')
stop_watch(sqlite3_file_performance)
# stop_watch(logger_performance, 'logger_performance()')
# stop_watch(logger_performance_sequential, 'logger_performance_sequential()')
# cProfile.run('logger_performance()')
# cProfile.run('sqlite3_file_performance()')
