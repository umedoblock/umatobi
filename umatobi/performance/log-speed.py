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
import datetime
import threading
import logging

threads_num = 1
records_num = 1
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

FORMAT = '%(asctime)-15s %(now)s %(level)-5s %(log_message)s %(message)s'
logging.basicConfig(format=FORMAT, filename='/tmp/loggerlogger.log', level=logging.INFO)
d = { 'clientip' : '192.168.0.1', 'user' : 'fbloggs' }
logger = logging.getLogger('loggerlogger')
# logger.warning('Protocol problem: %s', 'connection reset', extra=d)

class LoggerLogger(threading.Thread):
    def __init__(self, no, records_num, lock=None):
        threading.Thread.__init__(self)
      # print('LoggerLogger() filename =', dir(logging))
        self.no = no
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
        sql = 'insert into logs values(?,?,?,?)'
        print('conn.in_transaction 1 =', self.conn.in_transaction)
        for i in range(self.records_num):
            now = log_now()
            tup = (None, now, 'info', 'message {:08x}'.format(i))
#           print('tup =', tup)
            while True:
                try:
                    self.cur.execute(sql, tup)
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
# stop_watch(sqlite3_file_performance, 'sqlite3_file_performance()')
# stop_watch(logger_performance, 'logger_performance()')
stop_watch(logger_performance_sequential, 'logger_performance_sequential()')
# cProfile.run('logger_performance()')
# cProfile.run('sqlite3_file_performance()')
