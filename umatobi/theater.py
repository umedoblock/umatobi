import argparse
import sys

from simulator.screen import Screen
from simulator.screen import display_sample
from lib.args import args_theater
import simulator.sql

if __name__ == '__main__':
    args, db_path = args_theater('theater.')

    screen = Screen(sys.argv)

    if db_path or args.sample:
        if db_path:
            db = simulator.sql.SQL(db_path=db_path)
            print('db =', db)
          # screen.set_db(db)
        if args.sample:
            screen.set_display(display_sample)
        screen.start()
    elif args.show_timestamps:
        pass
    else:
        raise RuntimeError('at least, must use --sample option.')
