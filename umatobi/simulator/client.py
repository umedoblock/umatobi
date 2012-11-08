import sys, os
import threading
import sqlite3
import socket
import multiprocessing

from simulator.darkness import Darkness
from lib import make_logger, jbytes_becomes_dict

def make_darkness(config):
    '''darkness process を作成'''
    db_dir, darkness_id, \
    num_nodes, first_node_id, made_nodes, leave_there = \
            config.db_dir, config.darkness_id, \
            config.num_nodes, config.first_node_id, config.made_nodes, config.leave_there
    darkness_ = Darkness(db_dir, darkness_id,
                                  num_nodes, first_node_id, made_nodes, leave_there)
    darkness_.start()
  # darkness_.stop()

class DarknessConfig(object):
    '''darkness process と client が DarknessConfig を介して通信する。'''
    def __init__(self, db_dir, darkness_id, num_nodes, first_node_id, leave_there):
        self.db_dir = db_dir
        self.darkness_id = darkness_id
        self.first_node_id = first_node_id
        self.num_nodes = num_nodes
        # share with client and darknesses
        self.made_nodes = multiprocessing.Value('i', 0)
        # share with client and another darknesses
        self.leave_there = leave_there

class Client(object):
    SCHEMA = os.path.join(os.path.dirname(__file__), 'simulation_tables.schema')
    NODES_PER_DARKNESS = 4

    def __init__(self, watson, num_nodes, simulation_dir):
        '''\
        Clientは各PCに付き一つ作成する。
        watsonの待ち受けるUDP address = watson,
        作成するdarkness数 = num_darknesses,
        全ての simulate 結果を格納する simulation_dir と、
        watsonが起動した時間(start_up)を使用し、 simulation_dir以下に
        db_dir(=simulation_dir + '/' + start_up)を作成する。
        '''

        if isinstance(num_nodes, int) and num_nodes > 0:
            pass
        else:
            raise RuntimeError('num_nodes must be positive integer.')

        self.watson = watson
        self.simulation_dir = simulation_dir
        self.num_nodes = num_nodes
        # Client set positive integer to id in self._init_attrs().
        self.id = -1
        # TODO: #116 config, arg 等で NODES_PER_DARKNESS を
        #            変更できるようにする。
        self.nodes_per_darkness = self.NODES_PER_DARKNESS
        div, mod = divmod(self.num_nodes, self.nodes_per_darkness)
        if mod == 0:
            mod = self.nodes_per_darkness
        else:
            div += 1
        self.num_darkness = div
        self.last_darkness_make_nodes = mod
        self.total_created_nodes = 0
        self.darkness_processes = []

        # darkness に終了を告げる。
        self.leave_there = multiprocessing.Event()

        self.timeout_sec = 1
        socket.setdefaulttimeout(self.timeout_sec)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._init_attrs()

        self.logger = make_logger(self.db_dir, 'client', self.id)
        self.logger.info('----- {} log start -----'.format(self))
        self.logger.info('   watson = {}'.format(self.watson))
        self.logger.info('   db_dir = {}'.format(self.db_dir))
        self.logger.info('client_db = {}'.format(self.client_db))
        self.logger.info('----- client.{} initilized end -----'.
                          format(self.id))
        self.logger.debug('{} debug log test.'.format(self))
        self.logger.info('')

    def start(self):
        '''\
        Darknessを、たくさん作成する。
        作成後は、watsonから終了通知("break down")を受信するまで待機する。
        '''
        self.logger.info('Client(id={}) started!'.format(self.id))

        # 現在は使用しないけど、将来用に一応作成する。
      # self.conn = sqlite3.connect(self.client_db)
      # self.cur = self.conn.cursor()
        # けど、やっぱり comment out しておいた。
        # 必要となる、そのときまで待ちましょう。

        # Darkness が作成する node の数を設定する。
        nodes_per_darkness = self.nodes_per_darkness

        # for 内で darkness_process を作成し、
        # 順に darkness_processes に追加していく。
        for darkness_id in range(self.num_darkness):
            first_node_id = darkness_id * self.nodes_per_darkness
            if darkness_id == self.num_darkness - 1:
                # 最後に端数を作成？
                nodes_per_darkness = self.last_darkness_make_nodes
            self.logger.info('darkness id={}, nodes_per_darkness={}'.format(darkness_id, nodes_per_darkness))
            darkness_config = \
                DarknessConfig(self.db_dir, darkness_id, nodes_per_darkness, \
                               first_node_id, self.leave_there)
            darkness_process = \
                multiprocessing.Process(
                    target=make_darkness,
                    args=(darkness_config,)
                )
            darkness_process.config = darkness_config
            darkness_process.start()
            self.darkness_processes.append(darkness_process)

        # watson から終了通知("break down")が届くまで待機し続ける。
        # TODO: watson からの接続であると確認する。
        while True:
            try:
                recved, recved_addr = self.sock.recvfrom(1024)
            except socket.timeout:
                recved = b''
                continue

            if recved == b'break down.':
                self.logger.info('Client(id={}) got break down from {}.'.format(self.id, recved_addr))
                break

        # Client 終了処理開始。
        self._release()

    def join(self):
        '''threading.Thread を使用していた頃の名残。'''
        self.logger.info('Client(id={}) thread joined.'.format(self.id))

    def _release(self):
        '''\
        Client 終了処理。leave_thereにsignal を set することで、
        Clientの作成した Darkness達は一斉に終了処理を始める。
        '''
        # TODO: #100 client.db をwatsonに送りつける。

        self.logger.info(('Client(id={}) set signal to leave_there '
                          'for Darknesses.').format(self.id))
        self.leave_there.set()

        for darkness_p in self.darkness_processes:
            darkness_p.join()
            msg = 'Client(id={}), Darkness(id={}) process joined.'. \
                   format(self.id, darkness_p.config.darkness_id)
            self.logger.info(msg)
        self.logger.info('Client(id={}) thread released.'.format(self.id))

        for darkness_process in self.darkness_processes:
            self.total_created_nodes += darkness_process.config.made_nodes.value

        self.logger.info('Client(id={}) created num of nodes {}'.format(self.id, self.total_created_nodes))

    def _init_attrs(self):
        '''\
        watson に接続し、id, start_upを受信する。
        id は client.<id>.log として、log fileを作成するときに使用。
        start_up は db_dirを決定する際に使用する。
        '''
        d = self._hello_watson()
        if not d:
            self.sock.close()
            raise RuntimeError('client cannot say "I am Client." to watson who is {}'.format(self.watson))

        self.id = d['id']
        start_up = d['start_up']
        self.db_dir = os.path.join(self.simulation_dir, start_up)
        self.client_db = os.path.join(self.db_dir,
                                     'client.{}.db'.format(self.id))
        # sqlite3.connect() を実行するthreadと sqlite3.execute() を実行する
        # thread が異なると例外が起きてしまう。ここではattrを作成するだけ。
        self.conn = None # sqlite3.connect(self.client_db)
        self.cur = None # self.conn.cursor()

    def _hello_watson(self):
        '''\
        watsonに "I am Client." をUDPで送信し、watson起動時刻(start_up)、
        watsonへの接続順位(=id)をUDPで受信する。
        この時、受信するのはjson文字列。
        simulation 結果を格納する db_dir を作成するための情報を得る。
        db_dir 以下には、client.id.log, client.id.db 等を作成する。
        '''
        # TODO: #114 _hello_watson() に失敗した場合の例外処理を書く。
        tries = 0
        d = {}
        while tries < 3:
            try:
                self.sock.sendto(b'I am Client.', self.watson)
                recved_msg, who = self.sock.recvfrom(1024)
            except socket.timeout as raiz:
                tries += 1
                continue
          # if self.watson == who:
            d = jbytes_becomes_dict(recved_msg)
            break

      # print('who =', file=sys.stderr)
      # print(who, file=sys.stderr)
      # print('d =', file=sys.stderr)
      # print(d, file=sys.stderr)

        return d

    def __str__(self):
        return 'Client(id={})'.format(self.id)
