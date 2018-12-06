import json
import logging
import datetime
import time
import sys
import os
import threading
import sched

_here = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(_here, '..', 'simulator', 'simulation.schema')

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

def isoformat_time(t):
    "'return time format '2012-11-02T23:22:27.002481'"
    # milli, micro
    mmsecs = (t - int(t)) * 10 ** 6
    mmsecs = int(mmsecs)
    fmt = "%Y-%m-%dT%H:%M:%S"
  # datetime.datetime.strptime("2008-09-03T20:56:35.450686", "%Y-%m-%dT%H:%M:%S.%f")
    return time.strftime(fmt, time.localtime(t)) + '.{:06d}'.format(mmsecs)

def current_isoformat_time():
    now = time.time()
    return isoformat_time(now)

def isoformat_time_to_datetime(s):
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f")

def elapsed_time(start_up_orig):
    '''simulation 開始から現在までに経過したmilli秒数。'''
    now = datetime.datetime.now()
    # relativeCreated の時間単位がmillisecondsのため、
    # elapsed_time()もmilliseconds単位となるようにする。
    return int(((now - start_up_orig) * 1000).total_seconds())

#   %(relativeCreated)d Time in milliseconds when the LogRecord was created,
LOGGER_FMT = '%(relativeCreated)d %(name)s %(levelname)s %(message)s'

def make_logger2(log_dir=None, name='', level="INFO"):
    name = name.replace(".py", "")
    base_name = '.'.join([name, "log"])

    log_path = ""
    if log_dir is not None:
        log_path = os.path.join(log_dir, base_name)

    print(f"logging.getLogger(name={name}) in make_logger(name={name})")
    logger_obj = logging.getLogger(name)
    logger_obj.setLevel(level)

    # create formatter and add it to the handlers
    formatter = logging.Formatter(LOGGER_FMT + f"pid={os.getpid()}, thread_id={threading.get_ident()}")

    # create file handler which logs even debug messages
    fh = None
    if log_path:
        fh = logging.FileHandler(log_path)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger_obj.addHandler(fh)
        print(f"logger_obj.addHandler(fh={fh}) in make_logger(name={name})")
        # extra setting.
        logger_obj.log_path = log_path

    # create console handler with a higher log level
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(formatter)
    print(f"logger_obj.addHandler(ch={ch}) in make_logger(name={name})")
    logger_obj.addHandler(ch)
    print(f'logger_obj.manager.loggerDict={logger_obj.manager.loggerDict}')

    return logger_obj, fh, ch

def make_logger(log_dir=None, name='', id_=None, level="INFO"):
    name = name.replace(".py", "")
    log_path = ""
    if id_ is not None:
        name = f"{name}.{str(id_)}"
    if log_dir is not None:
        base_name = '.'.join([name, "log"])
        log_path = os.path.join(log_dir, base_name)

    print(f"logging.getLogger(name={name}) in make_logger(name={name})")
    logger_obj = logging.getLogger(name)
    print(f"==================logging.getLogger(logger_obj={logger_obj}, id(logger_obj)={id(logger_obj)} in make_logger(name={name})")
    logger_obj.setLevel(level)

    # create formatter and add it to the handlers
    formatter = logging.Formatter(LOGGER_FMT + f", pid={os.getpid()}, thread_id={threading.get_ident()}")

    # create file handler which logs even debug messages
    fh = None
    if log_path:
        fh = logging.FileHandler(log_path)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger_obj.addHandler(fh)
        print(f"logger_obj.addHandler(fh={fh}) in make_logger(name={name})")
        # extra setting.
        logger_obj.log_path = log_path

    # create console handler with a higher log level
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(formatter)
    print(f"==================logger_obj.addHandler(ch={ch}, id(ch)={id(ch)}) in make_logger(name={name})")
    logger_obj.addHandler(ch)
    print(f"++++++++++++++++++++++++++logger_obj(={logger_obj}.addHandler(ch={ch}) in make_logger(name={name})")
    print("logger_obj =", logger_obj)

    return logger_obj

def remove_logger(log_dir=None, name='', level="INFO"):
    name = name.replace(".py", "")
    print(f"logging.getLogger(name={name}) in remove_logger(name={name})")
    _logger = logging.getLogger(name)
    _logger.setLevel(level)

    formatter = logging.Formatter(LOGGER_FMT)

    log_path = ""
    if log_dir is not None:
        log_path = os.path.join(log_dir, base_name)
        fh = logging.FileHandler(log_path)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        print(f"_logger.removeHandler(fh={fh}) in remove_logger(name={name})")
        _logger.removeHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(formatter)
    print(f"_logger.removeHandler(ch={ch}) in remove_logger(name={name})")
    _logger.removeHandler(ch)

#   LOGGER_FMT = '%(asctime)s.%(msecs)03d %(levelname)s %(message)s'
#   LOGGER_DATEFMT = '%Y-%m-%dT%H:%M:%S'
#   formatter = logging.Formatter(LOGGER_FMT, datefmt=LOGGER_DATEFMT)
#   2012-11-02T23:01:10.002 INFO ----- watson log -----

#   # 2012-11-02T21:30:33.%f INFO ----- watson log -----
#   fmt = '%(asctime)s %(levelname)s %(message)s'
#   formatter = logging.Formatter(fmt, datefmt='%Y-%m-%dT%H:%M:%S.%f')

#   # 1351859998.124940.124 INFO ----- watson log -----
#   fmt = '%(created)f.%(msecs)d %(levelname)s %(message)s'
#   formatter = logging.Formatter(fmt, datefmt='%Y-%m-%dT%H:%M:%S.%f')

#   # 1351860066.285001 INFO ----- watson log -----
#   fmt = '%(created)f %(levelname)s %(message)s'
#   formatter = logging.Formatter(fmt, datefmt='%Y-%m-%dT%H:%M:%S.%f')

#   # 17 INFO ----- watson log -----
#   fmt = '%(relativeCreated)d %(levelname)s %(message)s'
#   formatter = logging.Formatter(fmt, datefmt='%Y-%m-%dT%H:%M:%S.%f')
