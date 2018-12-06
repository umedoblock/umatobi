import argparse
import sys, os

from simulator.screen import Screen
from simulator.screen import display_sample
from lib.args import args_theater
from lib.squares import _moving_squares
from lib import SCHEMA_PATH, make_logger
import simulator.sql
from lib.args import get_logger_args
global logger
logger_args = get_logger_args()
logger = make_logger(name=os.path.basename(__file__), level=logger_args.log_level)
logger.debug(f"__file__ = {__file__}")
logger.debug(f"__name__ = {__name__}")

if __name__ == '__main__':
    logger.info("theather start !")
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
    logger.info("theather finish !")
