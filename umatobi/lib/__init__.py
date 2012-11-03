import json
import logging
import time
import sys
import os

def dict_becomes_jbytes(d):
    js = json.dumps(d)
    jb = js.encode()
    return jb

def jbytes_becomes_dict(jb):
    js = jb.decode()
    d = json.loads(js)
    return d

def isoformat_time(t):
    "'return time format '2012-11-02T23:22:27.002'"
    msecs = (t - int(t)) * 1000
    msecs = int(msecs)
    fmt = "%Y-%m-%dT%H:%M:%S"
    return time.strftime(fmt, time.localtime(t)) + '.{:03d}'.format(msecs)

def current_isoformat_time():
    now = time.time()
    return isoformat_time(now)

def make_logger(log_dir='', name='', index=0, level=None):
    if not log_dir or not name in ('watson', 'client', 'darkness'):
        msg = 'log_dir(={}) must be available dir.'.format(log_dir)
        msg += 'name(={}) must be watson, client or darkness.'.format(name)
        raise RuntimeError(msg)

    ext = 'log'
    name_and_index = '.'.join([name, str(index)])
    base_name = '.'.join([name_and_index, ext])
    log_path = os.path.join(log_dir, base_name)

    logger = logging.getLogger(name_and_index)
    logger.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    fmt = '%(asctime)s.%(msecs)03d %(levelname)s %(message)s'
    formatter = logging.Formatter(fmt, datefmt='%Y-%m-%dT%H:%M:%S')
    # 2012-11-02T23:01:10.002 INFO ----- watson log -----

    # create file handler which logs even debug messages
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # create console handler with a higher log level
    # ch output log to sys.stderr
    ch = logging.StreamHandler(None)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # extra setting.
    logger.log_path = log_path
    if level is not None:
        fh.setLevel(level)
        ch.setLevel(level)

    return logger

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
