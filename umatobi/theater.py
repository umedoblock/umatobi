import argparse
import sys

from simulator.screen import Screen
from simulator.screen import display_sample
from lib.args import args_theater

if __name__ == '__main__':
    args, db_path = args_theater('theater.')

    screen = Screen(sys.argv)

    if db_path or args.sample:
        if db_path:
            print('db_path =', db_path)
            screen.set_display(None)
        if args.sample:
            screen.set_display(display_sample)
        screen.start()
    elif args.show_timestamps:
        pass
    else:
        raise RuntimeError('at least, must use --sample option.')

