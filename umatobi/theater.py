import argparse
import sys

from simulator.screen import Screen
from simulator.screen import display_sample
from lib.args import args_theater
from lib.squares import _moving_squares
from lib import SCHEMA_PATH
import simulator.sql

if __name__ == '__main__':
    args, db_path = args_theater('theater.')

    if db_path or args.sample or args.moving_squares:
        screen = Screen(sys.argv)

        if db_path:
            db = simulator.sql.SQL(db_path=db_path, schema_path=SCHEMA_PATH)
            screen.set_db(db)
            print('db =', db)
        if args.sample:
            screen.set_display(display_sample)
        elif args.moving_squares:
            screen.set_display(_moving_squares)
        screen.start()
    elif args.show_timestamps:
        pass
    else:
        raise RuntimeError('at least, must use --sample option.')
