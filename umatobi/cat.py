import argparse
import sys
import os

def args_xxx(description):
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

def args_log():
    parser = args_xxx(description='cat.py')
    parser.add_argument(# last argment, log file
                        metavar='f', dest='log_file',
                        nargs='?', default='',
                        help='watson.log, client.1.log or darkness.1.log, ...')
    args = parser.parse_args()
    return args

def show_timestamps(timestamps):
    timestamps.sort(reverse=True)
    print('{:>6s} timestamp'.format('index'))
    for i, d in enumerate(timestamps):
        if i == 0:
            print('{:>6d} {} newest'.format(i, d))
        else:
            print('{:>6d} {}'.format(i, d))

def gather_log_file(files):
    log_files = []
    for file_name in files:
        if file_name.endswith('.log'):
            log_files.append(file_name)
    return log_files

if __name__ == '__main__':
    # examples:
    # umatobi/cat.py --help
    # umatobi/cat.py --show-timestamps
    # umatobi/cat.py watson.log
    # umatobi/cat.py --index=1 client.1.log

    args = args_log()

    simulation_dir = args.simulation_dir
    log_file = args.log_file
    if args.show_timestamps or args.timestamp == '00000000T000000':
        timestamps = os.listdir(simulation_dir)

    if args.show_timestamps:
        print('simulation_dir = "{}"'.format(simulation_dir))
        show_timestamps(timestamps)
    else:
        if not log_file:
            message = 'log_file muse be watson.log, client.1.log, ...'
            raise RuntimeError(message)

        if args.timestamp == '00000000T000000':
            timestamp = timestamps[args.index]
        else:
            timestamp = args.timestamp
        dir_name = os.path.join(simulation_dir, timestamp)

        files = os.listdir(dir_name)
        log_files = gather_log_file(files)
        if not log_file in log_files:
            print('dir_name is "{}".'.format(dir_name))
            print('however, cannot use "{}" file'.format(log_file))
            print('please select log file in below log files.')
            print('    ' + '\n    '.join(log_files))
        else:
            path = os.path.join(dir_name, log_file)
            print('path =', path)
            with open(path) as f:
                for line in f:
                    print(line, end='')
