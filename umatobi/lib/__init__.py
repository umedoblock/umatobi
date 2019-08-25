import json
import datetime
import time
import sys
import os
import threading
import sched, configparser

from umatobi.constants import *

class Polling(threading.Thread):
    def __init__(self, polling_secs):
        threading.Thread.__init__(self)
        self.polling_secs = polling_secs
        # class sched.scheduler(timefunc, delayfunc)
        self._sche = sched.scheduler(time.time, time.sleep)
        self._sche.enter(self.polling_secs, 1, self._polling, ())

    def polling(self):
        raise NotImplementedError()

    def is_continue(self):
        raise NotImplementedError()

    def _polling(self):
        if self.is_continue():
            self.polling()
            self._sche.enter(self.polling_secs, 1, self._polling, ())

    def run(self):
        self._sche.run()

def get_db_from_schema():
    db = configparser.ConfigParser()
    with open(SCHEMA_PATH, encoding='utf-8') as schema:
        db.read_file(schema)
  # print('db =', db)
  # print('db.sections =', db.sections)
  # print('tuple(db.sections()) =', tuple(db.sections()))
  # db.keys() = ('DEFAULT', 'simulation', 'nodes', 'clients', 'growings')
    return db

def get_table_columns(table_name):
    return get_db_from_schema()[table_name]

def get_master_hand(start_up_time):
    return os.path.join(start_up_time, MASTER_HAND)

def get_master_hand_path(simulation_dir=SIMULATION_DIR, start_up_time='0000-00-00T000000'):
    return os.path.join(simulation_dir, get_master_hand(start_up_time))

def get_master_hand_path2(start_up_time, simulation_dir=SIMULATION_DIR):
    return os.path.join(simulation_dir, get_master_hand(start_up_time))

def validate_kwargs(st_barrier, kwargs):
    if st_barrier != kwargs.keys():
        st_unknown = kwargs.keys() - st_barrier
        st_must = st_barrier - kwargs.keys()
        message = ('unmatched st_barrier and kwargs.keys().\n'
                   'unknown keys are {},\n'
                   'must keys are {}').format(st_unknown, st_must)
        raise RuntimeError(message)

def bytes2dict(b):
    j = b.decode('utf-8')
    return json2dict(j)

def dict2bytes(d):
    j = dict2json(d)
    return j.encode('utf-8')

def dict2json(d):
    j = json.dumps(d)
    return j + '\n'

def json2dict(j):
    d = json.loads(j)
    return d

def tell_shutdown_time():
    shutdown_time = datetime.datetime.now()
    return shutdown_time

def make_start_up_orig():
    start_up_orig = datetime.datetime.now()
    return start_up_orig

def make_start_up_time():
    start_up_orig = make_start_up_orig()
    start_up_time = y15sformat_time(start_up_orig)
    return start_up_time

Y15S_FORMAT='%Y-%m-%dT%H%M%S'
def y15sformat_time(t):
    "'return time format '2012-11-02T232227'"
    return t.strftime(Y15S_FORMAT)

def current_y15sformat_time():
    now = datetime.datetime.now()
    return y15sformat_time(now)

def y15sformat_parse(s):
    return datetime.datetime.strptime(s, Y15S_FORMAT)

def get_passed_ms(start_up_orig):
    '''simulation 開始から現在までに経過したmilli秒数。'''
    now = datetime.datetime.now()
    # relativeCreated の時間単位がmsのため、
    # elapsed_time()もms単位となるようにする。
    return int(((now - start_up_orig) * 1000).total_seconds())

def elapsed_time(start_up_orig):
    '''simulation 開始から現在までに経過したmilli秒数。'''
    now = datetime.datetime.now()
    # relativeCreated の時間単位がmsのため、
    # elapsed_time()もms単位となるようにする。
    return int(((now - start_up_orig) * 1000).total_seconds())

def _normalize_ms(seconds):
    return int(seconds * 1000)

def get_passed_seconds(orig):
    e = datetime.datetime.now()
    return (e - orig).total_seconds()

def get_passed_ms(orig):
    passed_seconds = get_passed_seconds(orig)
    return _normalize_ms(passed_seconds)
