import argparse
import sys

from simulator.screen import Screen
from simulator.screen import display_sample

def args_():
    parser = argparse.ArgumentParser(description='screen.')

  # parser.add_argument('--recver-host', metavar='f', dest='recver_host',
  #                      nargs='?',
  #                      default='localhost',
  #                      help='my.server.net')
    parser.add_argument('--sample', dest='sample',
                         action='store_true', default=False,
                         help='sample')
  # parser.add_argument('--one-packet-size',
  #                      metavar='N', dest='one_packet_size',
  #                      type=int, nargs='?', default=(1024 * 4),
  #                      help='one packet size default is 4KO(4 * 1024)')
    parser.add_argument('--sql-path', metavar='f', dest='sql_path',
                         nargs='?',
                         default='',
                         help='simulate sql file path')
    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args = args_()

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
