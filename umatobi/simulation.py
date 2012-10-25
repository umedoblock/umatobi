import threading
import sys
import os
import struct
import math
import argparse
import socket
import datetime

from lib import make_logger, dict_becomes_jbytes
from simulator import Client

class Watson(threading.Thread):
    MAX_NODE_NUM=8

    def __init__(self, office, simulation_seconds, simulation_dir, start_up):
        threading.Thread.__init__(self)
        self.office = office
        self.simulation_seconds = simulation_seconds

      # self.simulation_dir = simulation_dir
        self.start_up = start_up
        self.db_dir = os.path.join(simulation_dir, self.start_up)
        self.simulation_db = os.path.join(self.db_dir, 'simulation.db')

      # self.watson_log = os.path.join(self.db_dir, 'watson.log')
        self.timeout_sec = 1
        self.nodes = []
        self.clients = []

        # socket() must set under setdefaulttimeout()
        socket.setdefaulttimeout(self.timeout_sec)
        self.watson = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.watson.bind(self.office)

        self.logger = make_logger(db_dir, 'watson')
        self.logger.info('----- watson log -----')
        self.logger.info('simulation_seconds={}'.format(simulation_seconds))

        # thread start!
        self.start()

    def run(self):
        self._s = datetime.datetime.today()

        self._wait_clients()
        self._release_clients()

    def join(self):
        threading.Thread.join(self)
        self.logger.info('watson thread joined.')

    def _wait_clients(self):
        count_inquiries = 0
        count_clients = 0

        while self.passed_time() < self.simulation_seconds:
            self.logger.info('passed time {:.3f}'.format(self.passed_time()))

            try:
              # print('================= count_inquiries =', count_inquiries)
              # print('self.watson.recvfrom() ==============================')
                text_message, phone_number = self.watson.recvfrom(1024)
            except socket.timeout:
              # print('phone_number timeouted.')
                phone_number = None

            if not phone_number:
                continue

            if text_message == b'I am Node.':
                csv = self.collect_nodes_as_csv()
                self.logger.info('realizing_nodes = "{}"'.format(csv))
                realizing_nodes = csv.encode()

                self.nodes.append(phone_number)
                if len(self.nodes) > self.MAX_NODE_NUM:
                    survived_node_index = len(self.nodes) - self.MAX_NODE_NUM
                    self.nodes = self.nodes[survived_node_index:]

                reply = realizing_nodes
            elif text_message == b'I am Client.':
                joined = datetime.datetime.today().strftime('%Y%m%dT%H%M%S')
                self.clients.append(phone_number)
                self.logger.info('Client[={}] came here.'.format(phone_number))
                sql = 'insert into clients (id, host, port, joined) values ({}, {}, {}, {})'.format(count_clients, phone_number[0],
                phone_number[1], joined)
                self.logger.debug('sql =', sql)
                d = {}
                d['no'] = count_clients
                d['start_up'] = self.start_up
                reply = dict_becomes_jbytes(d)
                count_clients += 1
                self.logger.debug('ok ok ok I am Client....')
            else:
                self.logger.debug('crazy man.')
                reply = b'Go back home.'

            self.watson.sendto(reply, phone_number)
            count_inquiries += 1


    def _release_clients(self):
        self.logger.info('simulation._release_clients()')
        for client in self.clients:
            result = b'break down.'
            self.watson.sendto(result, client)

    def collect_nodes_as_csv(self):
        csv = ','.join(['{}:{}'.format(*node) for node in self.nodes])
        return csv

    def passed_time(self):
        now = datetime.datetime.today()
        return (now - self._s).total_seconds()

    def __str__(self):
        return '{}:{}'.format(*self.office)

def args_():
    parser = argparse.ArgumentParser(description='simulation.')

    parser.add_argument('--init-node', metavar='f', dest='office',
                         nargs='?',
                         default='localhost:55555',
                         help='defalut is localhost:55555')
    parser.add_argument('--simulation-seconds', metavar='N',
                         dest='simulation_seconds',
                         type=int, nargs='?', default=15,
                         help='simulation seconds. defalut is 15')
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
    '''\
        watson, client, darkness が主要な process。
        watson: client からの依頼を待つ。
              : simulation 毎に一つ必要となる process。
        client: 多くの darkness を抱える。
              : simulation に参加するPC毎に一つ作成する。
        darkness: 漆黒の闇の中で蠢く謎の node の姿が！
                : client が起動する process。

        process 関係図

        watson-+-client.0
               |  |
               |  +-darkness.0
               |  | +-node.0
               |  | +-node.?
               |  | +-node.255
               |  |
               |  +-darkness.X
               |  | +-node.X
               |  |
               |  +-darkness.31
               |    +-node.7936
               |    +-node.?
               |    +-node.8191
               |
               +-client.?
        '''

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
    client = Client(office_, args.node_num, args.simulation_dir)

    # 実行開始

    # 終了処理
    client.join()
    watson.join()

  # print('node_num =', args.node_num)
  # for i in range(args.node_num):
  #     node = Node(args.host, args.port + i)
  #     print('node._keyID = {:08x}.'.format(node._keyID))
  #     node.info()
