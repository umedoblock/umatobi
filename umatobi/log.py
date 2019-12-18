# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import sys, os, argparse, logging

from umatobi.constants import *

__all__ = ['logger']

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
    ch = logging.StreamHandler(LOGGER_STREAM)
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger_obj.addHandler(ch)

    return logger_obj

# for logger ...
def _parse_logger_setting(parser):
    log_levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    parser.add_argument('--log-level',
                         metavar='LEVEL', dest='log_level',
                         choices=log_levels, default='INFO',
                         help=f'default INFO, must be in {log_levels}')
    parser.add_argument('--simulation-dir',
                         metavar='N', dest='simulation_dir',
                         nargs='?', default=UMATOBI_SIMULATION_DIR,
                         help='simulation directory.')
    return parser

# for logger ...
def get_logger_args():
    parser = argparse.ArgumentParser("logger setting")
    parser = _parse_logger_setting(parser)

    args, argv = parser.parse_known_args()
    # argv には，parser.add_argument() で追加していない
    # arg が格納されている。
    logger_args = args
    if logger_args.log_level in ("DEBUG", *range(1, 10 + 1)):
        # range(1, 10 + 1) means NOTSET < log_level <= logging.DEBUG
        print(f"argv={argv}", file=sys.stderr)

    return logger_args

logger_args = get_logger_args()
lags = logger_args
logger = make_logger(name=__package__, level=lags.log_level)
