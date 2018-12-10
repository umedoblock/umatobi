import argparse
import sys, os

from simulator.screen import Trailer, Screen
from simulator.screen import display_sample
from lib.args import args_theater
from lib.squares import _moving_squares
from lib import make_logger
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

    if args.sample or args.moving_squares:
        if args.sample:
            logger.info(f"Trailer(sys.argv={sys.argv}, display=display_sample)")
            trailer = Trailer(sys.argv, display=display_sample)
        elif args.moving_squares:
            logger.info(f"Trailer(sys.argv={sys.argv}, display=_moving_squares)")
            trailer = Trailer(sys.argv, display=_moving_squares)
        else:
            raise("no movie.")
        logger.info(f"{trailer}.start()")
        trailer.start()
    elif db_path:
        screen = Screen(sys.argv, db_path, display=Screen.display_main_thread)
        logger.info(f"{screen}.start()")
        screen.start()
    elif args.show_timestamps:
        pass
    else:
        raise RuntimeError('at least, must use --sample option.')
    logger.info("theather finish !")
