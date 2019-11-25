# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import sys
import os

from umatobi.lib.args import args_log

if __name__ == '__main__':
    # examples:
    # umatobi/cat.py --help
    # umatobi/cat.py --show-timestamps
    # umatobi/cat.py watson.log
    # umatobi/cat.py --index=1 client.1.log

    args, log_path = args_log('cat.py')

    if not log_path:
        sys.exit(0)

    print('log_path =', log_path)
    with open(log_path) as f:
        for line in f:
            print(line, end='')
