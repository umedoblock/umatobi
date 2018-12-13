import json
import logging
import datetime
import time
import sys
import os
import threading
import sched

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

def validate_kwargs(st_barrier, kwargs):
    if st_barrier != kwargs.keys():
        st_unknown = kwargs.keys() - st_barrier
        st_must = st_barrier - kwargs.keys()
        message = ('unmatched st_barrier and kwargs.keys().\n'
                   'unknown keys are {},\n'
                   'must keys are {}').format(st_unknown, st_must)
        raise RuntimeError(message)

def dict_becomes_jbytes(d):
    js = json.dumps(d) + "\n"
    jb = js.encode()
    return jb

def jtext_becomes_dict(jt):
    d = json.loads(jt)
    return d

def make_start_up_orig():
    start_up_orig = datetime.datetime.now()
    return start_up_orig

def tell_shutdown_time():
    shutdown_time = datetime.datetime.now()
    return shutdown_time

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

#   %(relativeCreated)d Time in ms when the LogRecord was created,
LOGGER_FMT = '%(relativeCreated)d %(name)s %(levelname)s %(filename)s %(funcName)s() - %(message)s'
LOGGER_SUFFIX = f" - process_id=%(process)d therad_id=%(thread)d"

def make_logger(log_dir=None, name='', id_=None, level="INFO"):
    name = name.replace(".py", "")
    log_path = ""
    if id_ is not None:
        name = f"{name}.{str(id_)}"
    if log_dir is not None:
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        base_name = '.'.join([name, "log"])
        log_path = os.path.join(log_dir, base_name)

    logger_obj = logging.getLogger(name)
    logger_obj.setLevel(level)

    # create formatter and add it to the handlers
    formatter = logging.Formatter(LOGGER_FMT + LOGGER_SUFFIX)

    # create file handler which logs even debug messages
    fh = None
    if log_path:
        fh = logging.FileHandler(log_path)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger_obj.addHandler(fh)
        # extra setting.
        logger_obj.log_path = log_path

    # create console handler with a higher log level
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger_obj.addHandler(ch)

    return logger_obj
