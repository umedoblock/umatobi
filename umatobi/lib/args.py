# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import argparse, re
import sys
import os

from umatobi.log import *
from umatobi.constants import *

def args_db(description):
    parser = _args_parse_basic(description)
    parser.add_argument(# db file
                        metavar='db file', dest='db_or_log_file',
                        nargs='?', default='defalut.db',
                        help='simulation.db, watson.db, or client.1.db, ...')
    parser.add_argument(# table name
                        metavar='table name', dest='table_name',
                        nargs='?', default='',
                        help='table name')
    args = parser.parse_args()
    db_path = _normalize_db_or_log_path(args)
    return args, db_path

def args_log(description):
    parser = _args_parse_basic(description)
    parser.add_argument(# last argment, log file
                        metavar='f', dest='db_or_log_file',
                        nargs='?', default='default.log',
                        help='watson.log, client.1.log or darkness.1.log, ...')
    args = parser.parse_args()
    log_path = _normalize_db_or_log_path(args)

    return args, log_path

def _get_simulation_db_path(args):
    args.db_or_log_file = SIMULATION_DB
    simulation_db_path = _normalize_db_or_log_path(args)
    return simulation_db_path

def args_theater(description):
    parser = _args_parse_basic(description)
    parser.add_argument('--sample', dest='sample',
                         action='store_true', default=False,
                         help='sample')
    parser.add_argument('--moving-squares', dest='moving_squares',
                         action='store_true', default=False,
                         help='moving squares')
    args = parser.parse_args()
    if args.sample or args.moving_squares:
        simulation_db_path = ''
    else:
        simulation_db_path = _get_simulation_db_path(args)

    return args, simulation_db_path

def args_make_simulation_db():
    parser = _args_parse_basic('make_simulation_db.py')
    args = parser.parse_args()
    simulation_db_path = _get_simulation_db_path(args)
    return args, simulation_db_path

def _args_parse_basic(description):
    parser = argparse.ArgumentParser(description)
    parser.add_argument('--show-timestamps', dest='show_timestamps',
                         action='store_true', default=False,
                         help='show index and directory timestamps')
    parser.add_argument('--simulation-dir',
                         metavar='N', dest='simulation_dir',
                         nargs='?', default=SIMULATION_DIR,
                         help='simulation directory.')
    parser.add_argument('--index',
                         metavar='N', dest='index',
                         type=int, nargs='?', default=0,
                         help='index default is 0')
    parser.add_argument('--timestamp',
                        metavar='timestamp', dest='timestamp',
                        nargs='?', default='00000000T000000',
                        help='example: 20121122T175422.480184')
    log_levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    parser.add_argument('--log-level',
                         metavar='LEVEL', dest='log_level',
                         choices=log_levels, default='INFO',
                         help=f'default INFO, must be in {log_levels}')
    return parser

def _show_timestamps(timestamps):
    print('{:>6s} timestamp'.format('index'))
    for i, d in enumerate(timestamps):
        if i == 0:
            print('{:>6d} {} newest'.format(i, d))
        else:
            print('{:>6d} {}'.format(i, d))

def _gather_db_or_log_files(files, db_or_log):
    dbs_or_logs = []
    for file_name in files:
        if file_name.endswith('.{}'.format(db_or_log)):
            dbs_or_logs.append(file_name)
    return dbs_or_logs

def _normalize_db_or_log_path(args):
    simulation_dir = args.simulation_dir
    db_or_log_file = args.db_or_log_file
    if sys.argv[0].endswith('cat.py'):
        db_or_log = 'log'
    else:
        db_or_log = 'db'

    if args.show_timestamps or args.timestamp == '00000000T000000':
        timestamps = os.listdir(simulation_dir)
        timestamps = [ts for ts in timestamps if re.match("\d{4}-\d{2}-\d{2}T", ts)]
        if not timestamps:
            print(f"{args.simulation_dir} directory 以下に simulation 結果が存在しませんでした。")
            sys.exit(0)
        timestamps.sort(reverse=True)
        logger.debug(f"timestamps={timestamps}")

    logger.debug(f"args={args}")
    db_or_log_path = ''
    if args.show_timestamps:
        logger.debug('simulation_dir = "{}"'.format(simulation_dir))
        _show_timestamps(timestamps)
    else:
        if not db_or_log_file:
            ss = '{}_file muse be watson.{}, client.1.{}, ...'
            message = ss.format(db_or_log, db_or_log, db_or_log)
            raise RuntimeError(message)
        if args.timestamp == '00000000T000000':
            try:
                timestamp = timestamps[args.index]
            except IndexError as raiz:
                _show_timestamps(timestamps)
                raise raiz
        else:
            timestamp = args.timestamp
        logger.debug(f"args.timestamp={args.timestamp}")
        logger.debug(f"timestamp={timestamp}")
        dir_name = os.path.join(simulation_dir, timestamp)

        logger.debug(f"dir_name={dir_name}")
        files = os.listdir(dir_name)
        dbs_or_logs = _gather_db_or_log_files(files, db_or_log)
        if db_or_log == 'db':
            dbs_or_logs.append(SIMULATION_DB)
        if db_or_log_file in dbs_or_logs:
            db_or_log_path = os.path.join(dir_name, db_or_log_file)
        else:
            print('dir_name is "{}".'.format(dir_name))
            print('however, cannot use "{}" file'.format(db_or_log_file))
            print('please select {} file in below {} files.'.format(db_or_log, db_or_log))
            print('    ' + '\n    '.join(dbs_or_logs))
    return db_or_log_path

  # 参考
  # parser.add_argument('--recver-host', metavar='f', dest='recver_host',
  #                      nargs='?',
  #                      default='localhost',
  #                      help='my.server.net')
  # parser.add_argument('--one-packet-size',
  #                      metavar='N', dest='one_packet_size',
  #                      type=int, nargs='?', default=(1024 * 4),
  #                      help='one packet size default is 4KO(4 * 1024)')
  # parser.add_argument('--show-timestamps', dest='show_timestamps',
  #                      action='store_true', default=False,
  #                      help='show index and directory timestamps')
