import argparse
import sys
import os

def args_db(description):
    parser = _args_parse_basic(description)
    parser.add_argument(# db file
                        metavar='db file', dest='db_or_log',
                        nargs='?', default='',
                        help='simulation.db, watson.db, or client.1.db, ...')
    parser.add_argument(# table name
                        metavar='table name', dest='table_name',
                        nargs='?', default='',
                        help='table name')
    args = parser.parse_args()
    db_path = _get_db_or_log_path(args, 'db')
    return args, db_path

def args_log(description):
    parser = _args_parse_basic(description)
    parser.add_argument(# last argment, log file
                        metavar='f', dest='db_or_log',
                        nargs='?', default='',
                        help='watson.log, client.1.log or darkness.1.log, ...')
    args = parser.parse_args()
    log_path = _get_db_or_log_path(args, 'log')

    return args, log_path

def args_theater(description):
    parser = _args_parse_basic(description)
    parser.add_argument(# db file
                        metavar='simulation db file', dest='db_or_log',
                        nargs='?', default='',
                        help='simulation.db, watson.db, or client.1.db, ...')
    parser.add_argument('--sample', dest='sample',
                         action='store_true', default=False,
                         help='sample')
    args.db_or_log = 'simulation.db'
    args = parser.parse_args()
    if args.sample:
        db_path = ''
    else:
        db_path = _get_db_or_log_path(args, 'db')

    return args, db_path

def _args_parse_basic(description):
    parser = argparse.ArgumentParser(description)
    parser.add_argument('--show-timestamps', dest='show_timestamps',
                         action='store_true', default=False,
                         help='show index and directory timestamps')
    parser.add_argument('--simulation-dir',
                         metavar='N', dest='simulation_dir',
                         nargs='?', default='./umatobi-simulation',
                         help='simulation directory.')
    parser.add_argument('--index',
                         metavar='N', dest='index',
                         type=int, nargs='?', default=0,
                         help='index default is 0')
    parser.add_argument('--timestamp',
                        metavar='timestamp', dest='timestamp',
                        nargs='?', default='00000000T000000',
                        help='example: 20121122T175422')
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

def _get_db_or_log_path(args, db_or_log):
    simulation_dir = args.simulation_dir
    db_or_log = args.db_or_log
    if args.show_timestamps or args.timestamp == '00000000T000000':
        timestamps = os.listdir(simulation_dir)
        timestamps.sort(reverse=True)

    db_or_log_path = ''
    if args.show_timestamps:
        print('simulation_dir = "{}"'.format(simulation_dir))
        _show_timestamps(timestamps)
    else:
        if not db_or_log:
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
        dir_name = os.path.join(simulation_dir, timestamp)

        files = os.listdir(dir_name)
        dbs_or_logs = _gather_db_or_log_files(files, db_or_log)
        if db_or_log in dbs_or_logs or db_or_log == 'simulation.db':
            db_or_log_path = os.path.join(dir_name, db_or_log)
        else:
            print('dir_name is "{}".'.format(dir_name))
            print('however, cannot use "{}" file'.format(db_or_log))
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
