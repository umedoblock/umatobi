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

def show_timestamps(timestamps):
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
        timestamps.sort(reverse=True)

    xxx_path = ''
    if args.show_timestamps:
        print('simulation_dir = "{}"'.format(simulation_dir))
        show_timestamps(timestamps)
    else:
        if not xxx_file:
            ss = '{}_file muse be watson.{}, client.1.{}, ...'
            message = ss.format(xxx, xxx, xxx)
            raise RuntimeError(message)
        if args.timestamp == '00000000T000000':
            try:
                timestamp = timestamps[args.index]
            except IndexError as raiz:
                show_timestamps(timestamps)
                raise raiz
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
