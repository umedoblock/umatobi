# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import argparse
import sys, os

from umatobi.log import *
from umatobi.simulator.screen import Trailer, Screen
from umatobi.simulator.screen import display_sample
from umatobi.lib.args import args_theater
from umatobi.lib.squares import _moving_squares

def are_there_any_seats():
    return "available"

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
