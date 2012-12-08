import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lib.args import args_xxx, get_xxx_path

def args_log():
    parser = args_xxx(description='cat.py')
    parser.add_argument(# last argment, log file
                        metavar='f', dest='xxx_file',
                        nargs='?', default='',
                        help='watson.log, client.1.log or darkness.1.log, ...')
    args = parser.parse_args()
    return args

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
