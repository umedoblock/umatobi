import threading
import os
import argparse
import datetime
import multiprocessing

from lib import make_logger, dict_becomes_jbytes
from simulator.client import Client
from simulator.watson import Watson

def make_client(office, node_num, simulation_dir):
    client = Client(office_, node_num, simulation_dir)
    client.start()
    client.join()

def args_():
    parser = argparse.ArgumentParser(description='simulation.')

    parser.add_argument('--init-node', metavar='f', dest='office',
                         nargs='?',
                         default='localhost:55555',
                         help='defalut is localhost:55555')
    parser.add_argument('--simulation-seconds', metavar='N',
                         dest='simulation_seconds',
                         type=int, nargs='?', default=10,
                         help='simulation seconds. defalut is 10')
  # parser.add_argument('--host', metavar='f', dest='host',
  #                      nargs='?',
  #                      default='localhost',
  #                      help='defalut is localhost')
  # parser.add_argument('--port',
  #                      metavar='N', dest='port',
  #                      type=int, nargs='?', default=10000,
  #                      help='first bind port.')
    parser.add_argument('--simulation-dir',
                         metavar='N', dest='simulation_dir',
                         nargs='?', default='./umatobi-simulation',
                         help='simulation directory.')
    parser.add_argument('--node-num',
                         metavar='N', dest='node_num',
                         type=int, nargs='?', default=5,
                         help='simulation node num.')
  # parser.add_argument('--sql-path', metavar='f', dest='sql_path',
  #                      nargs='?',
  #                      default='',
  #                      help='simulate sql file path')
    args = parser.parse_args()

    return args

def get_host_port(host_port):
    sp = host_port.split(':')
    host = sp[0]
    port = int(sp[1])
    return host, port

if __name__ == '__main__':
    # 引数の解析
    args = args_()
    office_ = get_host_port(args.office)

  # t = datetime.datetime.today()
  # >>> t
  # datetime.datetime(2012, 10, 8, 18, 4, 59, 659608)
  # >>> t.strftime('%Y%m%dT%H%M%S')
  # '20121008T180459'

  #
  #
  # simulation_dir
  # |-- 20121008T180459 # db_dir
  # |   |-- simulation.db # client.{0,1,2,...}.dbをmergeし、
  # |   |                 # watson が最後に作成する。
  # |   |-- watson.log  # watson の起動・停止・接続受付について
  # |   |-- client.0.db # client_db node が吐き出す SQL 文を書き込む。
  # |   `-- client.1.db # client_db
  # `-- 20121008T200822 # db_dir
  #     |-- client.0.db # client_db
  #     `-- client.1.db # client_db

    if not os.path.isdir(args.simulation_dir):
        os.makedirs(args.simulation_dir, exist_ok=True)

    start_up = datetime.datetime.today().strftime('%Y%m%dT%H%M%S')
    db_dir = os.path.join(args.simulation_dir, start_up)
    os.mkdir(db_dir)

    # 各 object を作成するなど。
    watson = Watson(office_, args.simulation_seconds,
                    args.simulation_dir, start_up)

    # Client will get start_up attribute in build_up_attrs()
    # after _hello_watson().
    client_process = multiprocessing.Process(target=make_client,
                                             args=(office_,
                                                   args.node_num,
                                                   args.simulation_dir))

    # 本当は client_process を、ここで作らなくてもいい。
    # module の独立から考えると、むしろ作らない方が望ましいのだけど、
    # terminal 上で、別 process を起動させる手間を考えると楽なので、
    # ここで作ってしまう。 Makefile とか作りたくない。。。
    client_process.start()
    client_process.join()

    # 終了処理
    watson.join()
