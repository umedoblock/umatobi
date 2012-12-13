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
    js = json.dumps(d)
    jb = js.encode()
    return jb

def jbytes_becomes_dict(jb):
    js = jb.decode()
    d = json.loads(js)
    return d

def make_start_up_time():
    start_up_time = datetime.datetime.now()
    return start_up_time

def isoformat_time(t):
    "'return time format '2012-11-02T23:22:27.002481'"
    # milli, micro
    mmsecs = (t - int(t)) * 10 ** 6
    mmsecs = int(mmsecs)
    fmt = "%Y-%m-%dT%H:%M:%S"
    return time.strftime(fmt, time.localtime(t)) + '.{:06d}'.format(mmsecs)

def current_isoformat_time():
    now = time.time()
    return isoformat_time(now)

def isoformat_time_to_datetime(s):
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f")

def elapsed_time(self):
    '''simulation 開始から現在までに経過したmilli秒数。'''
    now = datetime.datetime.now()
    # relativeCreated の時間単位がmillisecondsのため、
    # elapsed_time()もmilliseconds単位となるようにする。
    return int(((now - self.start_up_time) * 1000).total_seconds())

def datetime_to_float(dt):
    float_ = time.mktime(dt.timetuple()) + (dt.microsecond / (10 ** 6))
    return float_

def set_logging_startTime_from_start_up_time(self):
  # print('time.time() = {}'.format(time.time()))
  # print('self.start_up_time = {}'.format(self.start_up_time))
  # print('self.iso_start_up_time = {}'.format(self.iso_start_up_time))
  # print('logging._startTime1 = {}'.format(logging._startTime))
  # _startTime = time.time()
  # self.relativeCreated = (self.created - _startTime) * 1000
    logging._startTime = datetime_to_float(self.start_up_time)
  # print('logging._startTime2 = {}'.format(logging._startTime))

#   %(relativeCreated)d Time in milliseconds when the LogRecord was created,
LOGGER_FMT = '%(relativeCreated)d %(levelname)s %(message)s'

def make_logger(log_dir='', name='', index=0, level=None):
    if not log_dir or not name in ('watson', 'client', 'darkness'):
        msg = 'log_dir(={}) must be available dir.'.format(log_dir)
        msg += 'name(={}) must be watson, client or darkness.'.format(name)
        raise RuntimeError(msg)

    if name == 'watson':
        name_and_index = name
    else:
        name_and_index = '.'.join([name, str(index)])
    ext = 'log'
    base_name = '.'.join([name_and_index, ext])
    log_path = os.path.join(log_dir, base_name)

    logger = logging.getLogger(name_and_index)
    logger.setLevel(level)

    # create formatter and add it to the handlers
    formatter = logging.Formatter(LOGGER_FMT)

    # create file handler which logs even debug messages
    fh = logging.FileHandler(log_path)
    fh.setLevel(level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # create console handler with a higher log level
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # extra setting.
    logger.log_path = log_path
    if level is not None:
        fh.setLevel(level)
        ch.setLevel(level)

    return logger

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
