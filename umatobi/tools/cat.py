import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lib.args import args_log

if __name__ == '__main__':
    # examples:
    # umatobi/cat.py --help
    # umatobi/cat.py --show-timestamps
    # umatobi/cat.py watson.log
    # umatobi/cat.py --index=1 client.1.log

    args, log_path = args_log('cat.py')

    if log_path:
        print('log_path =', log_path)
        with open(log_path) as f:
            for line in f:
                print(line, end='')
