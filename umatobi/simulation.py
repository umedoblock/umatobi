import threading
import os
import argparse
import datetime
import multiprocessing

from lib import make_logger, make_start_up_orig, tell_shutdown_time
from lib.args import get_logger_args
from simulator.client import Client
from simulator.watson import Watson

def make_client(watson_office_addr, num_nodes):
    client = Client(watson_office_addr, num_nodes)
    client.start()
    client.join()

def args_():
    parser = argparse.ArgumentParser(description='simulation.')

    parser.add_argument('--watson-office-addr', metavar='f', dest='watson_office_addr',
                         nargs='?',
                         default='localhost:55555',
                         help='defalut watson office addr is localhost:55555')
    parser.add_argument('--simulation-seconds', metavar='N',
                         dest='simulation_seconds',
                         type=int, nargs='?', default=10,
                         help='simulation seconds. defalut is 10')
    parser.add_argument('--simulation-dir',
                         metavar='N', dest='simulation_dir',
                         nargs='?', default='./umatobi-simulation',
                         help='simulation directory.')
    parser.add_argument('--num-nodes',
                         metavar='N', dest='num_nodes',
                         type=int, nargs='?', default=5,
                         help='simulation num of nodes.')
    _log_levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    log_levels = list(_log_levels)
    log_levels.insert(-1, 'or')
    help_log_level = ' '.join(log_levels) + ' (dedfault: INFO) ' + \
                     'case insensitive'
    parser.add_argument('--log-level',
                         metavar='LEVEL', dest='log_level',
                         choices=_log_levels, default='INFO',
                         help=help_log_level)
    args = parser.parse_args()
    args.log_level = args.log_level.upper()
    if not (args.log_level in _log_levels):
        message = '--log-level=LEVEL must be {}.'.format(' '.join(log_levels))
        raise argparse.ArgumentTypeError(message)
    return args

def get_host_port(host_port):
    sp = host_port.split(':')
    host = sp[0]
    port = int(sp[1])
    return host, port

if __name__ == '__main__':
    logger_args = get_logger_args()
    start_up_orig = make_start_up_orig()
    start_up_time = start_up_orig.isoformat()

    logger = make_logger(log_dir=logger_args.simulation_dir, \
                         name="admin", \
                         level=logger_args.log_level)
    logger.info(f"start_up_time={start_up_time}")
    logger.info("simulation start !")

    # 引数の解析
    args = args_()

    watson_office_addr = get_host_port(args.watson_office_addr)

  # t = datetime.datetime.now()
  # >>> t
  # datetime.datetime(2012, 10, 8, 18, 4, 59, 659608)
  # >>> t.strftime('%Y%m%dT%H%M%S')
  # '20121008T180459'

  #
  #
  # simulation_dir
  # |-- 20121008T180459 # isoformat(), dirname = simulation_dir + isoformat()
  # |   |-- simulation.db # client.{0,1,2,...}.dbをmergeし、
  # |   |                 # watson が最後に作成する。
  # |   |-- watson.log  # watson の起動・停止・接続受付について
  # |   |-- client.0.db # client_db node が吐き出す SQL 文を書き込む。
  # |   `-- client.1.db # client_db
  # `-- 20121008T200822 # isoformat()
  #     |-- client.0.db # client_db
  #     `-- client.1.db # client_db

    simulation_dir = args.simulation_dir

  # simulation_dir 以下に起動時刻を元にした dir_name を作成する。
  # dir_name 以下に、simulation結果の生成物、
  # simulation.db, watson.0.log, client.0.log ...
  # を作成する。
    dir_name = os.path.join(simulation_dir, start_up_time)

    if not os.path.isdir(dir_name): os.makedirs(dir_name, exist_ok=True)

    # 各 object を作成するなど。
    watson = Watson(watson_office_addr, args.simulation_seconds,
                    start_up_orig,
                    dir_name, args.log_level)

    # Watson start!
    watson.start()
    watson.watson_office_addr_assigned.wait()
    watson_office_addr = watson.watson_office_addr

    # Client will get start_up_time attribute in build_up_attrs()
    # after _hello_watson().
    client_process = multiprocessing.Process(target=make_client,
                                             args=(watson_office_addr,
                                                   args.num_nodes))

    # 本当は client_process を、ここで作らなくてもいい。
    # module の独立から考えると、むしろ作らない方が望ましいのだけど、
    # terminal 上で、別 process を起動させる手間を考えると楽なので、
    # ここで作ってしまう。 Makefile とか作りたくない。。。
    client_process.start()
    logger.info(f"client_process.pid={client_process.pid}")
    client_process.join()

    # 終了処理
    watson.join()

    logger.info("simulation end !")
    shutdown_time = tell_shutdown_time()
    logger.info(f"shutdown_time={shutdown_time}")
