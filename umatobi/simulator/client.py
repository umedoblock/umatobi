import sys, os
import threading
import sqlite3
import socket
import multiprocessing

from . import darkness
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lib import make_logger, jbytes_becomes_dict

def make_darkness(config):
    '''darkness process を作成'''
    db_dir, no, \
    num_nodes, made_nodes, leave_there = \
            config.db_dir, config.no, \
            config.num_nodes, config.made_nodes, config.leave_there
    darkness_ = darkness.Darkness(db_dir, no,
                                  num_nodes, made_nodes, leave_there)
    darkness_.start()
  # darkness_.stop()

class DarknessConfig(object):
    '''darkness process と client が DarknessConfig を介して通信する。'''
    def __init__(self, db_dir, no, num_nodes, leave_there):
        self.db_dir = db_dir
        self.no = no
        self.num_nodes = num_nodes
        # share with client and darknesses
        self.made_nodes = multiprocessing.Value('i', 0)
        # share with client and another darknesses
        self.leave_there = leave_there

class Client(object):
    SCHEMA = os.path.join(os.path.dirname(__file__), 'simulation_tables.schema')

    def __init__(self, watson, num_nodes, simulation_dir):
        '''\
        Clientは各PCに付き一つ作成する。
        watsonの待ち受けるUDP address = watson,
        作成するdarkness数 = num_darknesses,
        全ての simulate 結果を格納する simulation_dir と、
        watsonが起動した時間(start_up)を使用し、 simulation_dir以下に
        db_dir(=simulation_dir + '/' + start_up)を作成する。
        '''
        self.watson = watson
        self.simulation_dir = simulation_dir
        self.num_darkness = 2
        self.num_nodes = 4
        self.total_nodes = 0
        self.darkness_processes = []

        # darkness に終了を告げる。
        self.leave_there = multiprocessing.Event()

        self.timeout_sec = 1
        socket.setdefaulttimeout(self.timeout_sec)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._init_attrs()

        self.logger = make_logger(self.db_dir, 'client', self.no)
        self.logger.info('----- client.{} log start -----'.format(self.no))
        self.logger.info('   watson = {}'.format(self.watson))
        self.logger.info('   db_dir = {}'.format(self.db_dir))
        self.logger.info('client_db = {}'.format(self.client_db))
        self.logger.info('----- client.{} initilized end -----'.
                          format(self.no))
        self.logger.info('')

    def start(self):
        '''\
        Darknessを、たくさん作成する。
        作成後は、watsonから終了通知("break down")を受信するまで待機する。
        '''
        self.logger.info('Client(no={}) started!'.format(self.no))

        # for 内で darkness_process を作成し、
        # 順に darkness_processes に追加していく。
        for no in range(self.num_darkness):
            darkness_config = \
                DarknessConfig(self.db_dir, no, self.num_nodes, \
                               self.leave_there)
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
                self.logger.info('Client(no={}) got break down from {}.'.format(self.no, recved_addr))
                break

        # Client 終了処理開始。
        self._release()

    def join(self):
        '''threading.Thread を使用していた頃の名残。'''
        self.logger.info('Client(no={}) thread joined.'.format(self.no))

    def _release(self):
        '''\
        Client 終了処理。leave_thereにsignal を set することで、
        Clientの作成した Darkness達は一斉に終了処理を始める。
        '''
        # TODO: #100 client.db をwatsonに送りつける。

        self.logger.info(('Client(no={}) set signal to leave_there '
                          'for Darknesses.').format(self.no))
        self.leave_there.set()

        for darkness_p in self.darkness_processes:
            darkness_p.join()
            msg = 'Client(no={}), Darkness(no={}) process joined.'. \
                   format(self.no, darkness_p.config.no)
            self.logger.info(msg)
        self.logger.info('Client(no={}) thread released.'.format(self.no))

        for darkness_process in self.darkness_processes:
            self.total_nodes += darkness_process.config.made_nodes.value

        self.logger.info('Client(no={}) created num of nodes {}'.format(self.no, self.total_nodes))

    def _init_attrs(self):
        '''\
        watson に接続し、no, start_upを受信する。
        no は client.<no>.log として、log fileを作成するときに使用。
        start_up は db_dirを決定する際に使用する。
        '''
        d = self._hello_watson()
        if not d:
            raise RuntimeError('client._hello_watson() return None object. watson is {}'.format(self.watson))

        self.no = d['no']
        start_up = d['start_up']
        self.db_dir = os.path.join(self.simulation_dir, start_up)
        self.client_db = os.path.join(self.db_dir,
                                     'client.{}.db'.format(self.no))
        self.conn = sqlite3.connect(self.client_db)

    def _hello_watson(self):
        '''\
        watsonに "I am Client." をUDPで送信し、watson起動時刻(start_up)、
        watsonへの接続順位(=no)をUDPで受信する。
        この時、受信するのはjson文字列。
        simulation 結果を格納する db_dir を作成するための情報を得る。
        db_dir 以下には、client.no.log, client.no.db 等を作成する。
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
