import threading
import sys
import os
import struct
import math
import argparse
import socket
import datetime

# sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
# from umatobi.lib import formula

from simulator import Relay

import json
def dict_becomes_jbytes(d):
    js = json.dumps(d)
    jb = js.encode()
    return jb

class InitNode(threading.Thread):
    MAX_NODE_NUM=8

    def __init__(self, init_node, simulation_seconds, simulation_dir, start_up):
        threading.Thread.__init__(self)
        self.init_node = init_node
        self.simulation_seconds = simulation_seconds

      # self.simulation_dir = simulation_dir
        self.start_up = start_up
        self.db_dir = os.path.join(simulation_dir, self.start_up)
        self.simulation_db = os.path.join(self.db_dir, 'simulation.db')
        self.timeout_sec = 1
        self.nodes = []
        self.relays = []

        # socket() must set under setdefaulttimeout()
        socket.setdefaulttimeout(self.timeout_sec)
        self.watson = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.watson.bind(self.init_node)

    def run(self):
        self._s = datetime.datetime.today()

        self._wait_clients()
        self._release_clients()

    def _wait_clients(self):
        count_clients = 0
        count_relays = 0

        while self.passed_time() < self.simulation_seconds:
            print('\rpassed time {:.3f}'.format(self.passed_time()), end='')

            try:
                print('================= count_clients =', count_clients)
                print('self.watson.recvfrom() ==============================')
                client_say, client = self.watson.recvfrom(1024)
            except socket.timeout:
                print('relay timeouted.')
                client = None

            if not client:
                continue

            print()
            if client_say == b'I am Node.':
                csv = self.collect_nodes_as_csv()
                print('realizing_nodes = "{}"'.format(csv))
                realizing_nodes = csv.encode()

                self.nodes.append(client)
                if len(self.nodes) > self.MAX_NODE_NUM:
                    survived_node_index = len(self.nodes) - self.MAX_NODE_NUM
                    self.nodes = self.nodes[survived_node_index:]

                reply = realizing_nodes
            elif client_say == b'I am Relay.':
                joined = datetime.datetime.today().strftime('%Y%m%dT%H%M%S')
                self.relays.append(client)
                print('Relay[={}] came here.'.format(client))
                sql = 'insert into relays (id, host, port, joined) values ({}, {}, {}, {})'.format(count_relays, client[0], client[1], joined)
                print('sql =', sql)
                d = {}
                d['no'] = count_relays
                d['start_up'] = self.start_up
                reply = dict_becomes_jbytes(d)
                count_relays += 1
                print('ok ok ok I am Relay....')
            else:
                print('crazy man.')
                reply = b'Go back home.'

            self.watson.sendto(reply, client)
            count_clients += 1

        print()

    def _release_clients(self):
        print('simulation._release_clients()')
        for relay in self.relays:
            result = b'break down.'
          # self.watson.sendto(result, relay)

    def collect_nodes_as_csv(self):
        csv = ','.join(['{}:{}'.format(*node) for node in self.nodes])
        return csv

    def passed_time(self):
        now = datetime.datetime.today()
        return (now - self._s).total_seconds()

    def __str__(self):
        return '{}:{}'.format(*self.init_node)

def args_():
    parser = argparse.ArgumentParser(description='simulation.')

    parser.add_argument('--init-node', metavar='f', dest='init_node',
                         nargs='?',
                         default='localhost:55555',
                         help='defalut is localhost:55555')
    parser.add_argument('--simulation-seconds', metavar='N',
                         dest='simulation_seconds',
                         type=int, nargs='?', default=180,
                         help='simulation seconds. defalut is 180')
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
    init_node_ = get_host_port(args.init_node)

  # t = datetime.datetime.today()
  # >>> t
  # datetime.datetime(2012, 10, 8, 18, 4, 59, 659608)
  # >>> t.strftime('%Y%m%dT%H%M%S')
  # '20121008T180459'

  # simulation_dir
  # |-- 20121008T180459 # db_dir
  # |   |-- simulation.db # so no man ma
  # |   |-- relay.0.db # relay_db
  # |   `-- relay.1.db # relay_db
  # `-- 20121008T200822 # db_dir
  #     |-- relay.0.db # relay_db
  #     `-- relay.1.db # relay_db

    if not os.path.isdir(args.simulation_dir):
        os.makedirs(args.simulation_dir, exist_ok=True)

    start_up = datetime.datetime.today().strftime('%Y%m%dT%H%M%S')
    db_dir = os.path.join(args.simulation_dir, start_up)
    os.mkdir(db_dir)

    # 各 object を作成するなど。
    init_node = InitNode(init_node_, args.simulation_seconds, args.simulation_dir, start_up)
    print('init_node 0 =', init_node)
    print('init_node_={}'.format(init_node))
    print('simulation_seconds={}'.format(args.simulation_seconds))

    # Relay will get start_up attribute in build_up_attrs()
    # after _hello_watson().
    relay = Relay(init_node_, args.node_num, args.simulation_dir)

    # 実行開始
    init_node.start()

    relay.build_up_attrs()
    print('type(init_node) 3 =', type(init_node))

    print('init_node.join() waiting ...')
    # 終了処理
    init_node.join()

  # print('node_num =', args.node_num)
  # for i in range(args.node_num):
  #     node = Node(args.host, args.port + i)
  #     print('node._keyID = {:08x}.'.format(node._keyID))
  #     node.info()

    print('init node initilized.')
