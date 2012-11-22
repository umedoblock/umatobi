import argparse
import sys
import os

def args_():
    parser = argparse.ArgumentParser(description='cat.py')
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
    parser.add_argument(# last argment, base name
                        metavar='base_name', dest='base_name',
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

    args = args_()

    simulation_dir = args.simulation_dir
    base_name = args.base_name
    if args.show_timestamps or args.timestamp == '00000000T000000':
        timestamps = os.listdir(simulation_dir)

    if args.show_timestamps:
        print('simulation_dir = "{}"'.format(simulation_dir))
        show_timestamps(timestamps)
    else:
        if not args.base_name:
            message = 'base_name muse be watson.log, client.1.log, ...'
            raise RuntimeError(message)

        if args.timestamp == '00000000T000000':
            timestamp = timestamps[args.index]
        else:
            timestamp = args.timestamp
        dir_name = os.path.join(simulation_dir, timestamp)

        files = os.listdir(dir_name)
        log_files = gather_log_file(files)
        if not base_name in log_files:
            print('dir_name is "{}".'.format(dir_name))
            print('however, cannot use "{}" file'.format(base_name))
            print('please select log file in below log files.')
            print('    ' + '\n    '.join(log_files))
        else:
            path = os.path.join(dir_name, base_name)
            print('path =', path)
            with open(path) as f:
                for line in f:
                    print(line, end='')
