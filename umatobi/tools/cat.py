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
                        metavar='f', dest='xxx_file',
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

def gather_xxx_file(files, xxx):
    xxx_files = []
    for file_name in files:
        if file_name.endswith('.{}'.format(xxx)):
            xxx_files.append(file_name)
    return xxx_files

def get_xxx_path(args, xxx):
    simulation_dir = args.simulation_dir
    xxx_file = args.xxx_file
    if args.show_timestamps or args.timestamp == '00000000T000000':
        timestamps = os.listdir(simulation_dir)

    xxx_path = ''
    if args.show_timestamps:
        print('simulation_dir = "{}"'.format(simulation_dir))
        show_timestamps(timestamps)
    else:
        if not xxx_file:
            if xxx == 'log':
                message = 'log_file muse be watson.log, client.1.log, ...'
            raise RuntimeError(message)

        if args.timestamp == '00000000T000000':
            timestamp = timestamps[args.index]
        else:
            timestamp = args.timestamp
        dir_name = os.path.join(simulation_dir, timestamp)

        files = os.listdir(dir_name)
        xxx_files = gather_xxx_file(files, xxx)
        if not xxx_file in xxx_files:
            print('dir_name is "{}".'.format(dir_name))
            print('however, cannot use "{}" file'.format(xxx_file))
            print('please select {} file in below {} files.'.format(xxx, xxx))
            print('    ' + '\n    '.join(xxx_files))
        else:
            xxx_path = os.path.join(dir_name, xxx_file)
    return xxx_path

if __name__ == '__main__':
    # examples:
    # umatobi/cat.py --help
    # umatobi/cat.py --show-timestamps
    # umatobi/cat.py watson.log
    # umatobi/cat.py --index=1 client.1.log

    args = args_log()
    log_path = get_xxx_path(args, 'log')

    if log_path:
        print('log_path =', log_path)
        with open(log_path) as f:
            for line in f:
                print(line, end='')
