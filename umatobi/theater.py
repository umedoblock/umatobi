import argparse
import sys

from simulator.screen import Screen
from simulator.screen import display_sample
from lib.args import args_theater

if __name__ == '__main__':
    args = args_theater('theater.')

    screen = Screen(sys.argv)

    if args.sample:
        screen.set_display(display_sample)
  # elif args.sql_path:
  #     raise RuntimeError('must set --sample.')
  #     f = open(args.sql_path)
  #     screen.take_resource(f)
  #     screen.set_display(display_sql)
    else:
        raise RuntimeError('at least, must use --sample option.')

    screen.start()
