import sys, os
import threading
import sqlite3
import socket
import multiprocessing

from simulator.darkness import Darkness
import simulator.sql
from lib import make_logger, jbytes_becomes_dict, dict_becomes_jbytes
from lib import SCHEMA_PATH, isoformat_time_to_datetime

def make_darkness(d_config):
    '''darkness process を作成'''
    darkness_ = Darkness(**d_config)
    darkness_.start()

def make_darkness_d_config(db_dir, darkness_id, client_id, log_level,
                           start_up_time,
                           num_nodes, first_node_id, leave_there):
    '''client と darkness process が DarknessConfig を介して通信する。'''
    d = {}
    d['db_dir'] = db_dir
    d['id'] = darkness_id
    d['client_id'] = client_id
    d['log_level'] = log_level
    d['start_up_time'] = start_up_time
    d['first_node_id'] = first_node_id
    d['num_nodes'] = num_nodes
    # share with client and darknesses
    d['made_nodes'] = multiprocessing.Value('i', 0)
    # share with client and another darknesses
    d['leave_there'] = leave_there

    return d

class Client(object):
    NODES_PER_DARKNESS = 4

    def __init__(self, watson, num_nodes, simulation_dir):
        '''\
        Clientは各PCに付き一つ作成する。
        watsonの待ち受けるUDP address = watson,
        作成するdarkness数 = num_darknesses,
        全ての simulate 結果を格納する simulation_dir と、
        watsonが起動した時間(start_up_time)を使用し、 simulation_dir以下に
        db_dir(=simulation_dir + '/' + start_up_time)を作成する。
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
        self.nodes_per_darkness = self.NODES_PER_DARKNESS
        self.node_index = -1
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
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        _d_init_attrs = self._init_attrs()

        self.logger = make_logger(self.db_dir, 'client', self.id,
                                  level=self.log_level)
        self.logger.info('----- {} log start -----'.format(self))
        self.logger.info('   watson = {}'.format(self.watson))
        self.logger.info('   db_dir = {}'.format(self.db_dir))
        self.logger.info('client_db_path = {}'.format(self.client_db_path))
        self.logger.info('----- client.{} initilized end -----'.
                          format(self.id))
        self.logger.debug('{} d={}'.format(self, _d_init_attrs))
        self.logger.debug('{} node_index={}'.format(self, self.node_index))
        self.logger.debug('{} debug log test.'.format(self))
        self.logger.info('')

    def start(self):
        '''\
        Darknessを、たくさん作成する。
        作成後は、watsonから終了通知("break down")を受信するまで待機する。
        '''
        self.logger.info('Client(id={}) started!'.format(self.id))
        self.client_db = simulator.sql.SQL(owner=self,
                                           db_path=self.client_db_path,
                                           schema_path=self.schema_path)
        self.client_db.create_db()
        self.logger.info('{} client_db.create_db().'.format(self))
        self.client_db.create_table('growings')
        self.logger.info('{} client_db.create_table(\'growings\').'.format(self))

        # Darkness が作成する node の数を設定する。
        nodes_per_darkness = self.nodes_per_darkness

        # for 内で darkness_process を作成し、
        # 順に darkness_processes に追加していく。
        for darkness_id in range(1, self.num_darkness + 1):
            first_node_id = self.node_index + \
                            (darkness_id - 1) * self.nodes_per_darkness
            if darkness_id == self.num_darkness:
                # 最後に端数を作成？
                nodes_per_darkness = self.last_darkness_make_nodes
            self.logger.info('darkness id={}, nodes_per_darkness={}'.format(darkness_id, nodes_per_darkness))
            client_id = self.id
            darkness_d_config = \
                make_darkness_d_config(self.db_dir, darkness_id, client_id,
                               self.log_level, self.start_up_time,
                               nodes_per_darkness,
                               first_node_id, self.leave_there)
            darkness_process = \
                multiprocessing.Process(
                    target=make_darkness,
                    args=(darkness_d_config,),
                )
            darkness_process.d_config = darkness_d_config
            darkness_process.start()
            self.darkness_processes.append(darkness_process)

        # watson から終了通知("break down")が届くまで待機し続ける。
        # TODO: #149 watson からの接続であると確認する。
        while True:
            try:
                recved, recved_addr = self._sock.recvfrom(1024)
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
        self.logger.info(('Client(id={}) set signal to leave_there '
                          'for Darknesses.').format(self.id))
        self.leave_there.set()

        for darkness_p in self.darkness_processes:
            darkness_p.join()
            msg = 'Client(id={}), Darkness(id={}) process joined.'. \
                   format(self.id, darkness_p.d_config['id'])
            self.logger.info(msg)
        self.logger.info('Client(id={}) thread released.'.format(self.id))

        self.client_db.close()
        self.logger.info('{} client_db.close().'.format(self))
      # self.logger.error('self._sock.getsockname() =', ('127.0.0.1', 20000))
        # ip のみ比較、 compare only ip
        if False and self._sock.getsockname()[0] != self.watson[0]:
            self.logger.error('TODO: #100 client.db をwatsonに送りつける。')
            # _sock=('0.0.0.0', 22343), watson=('localhost', 55555)
            message = '{} _sock={}, watson={}'. \
                       format(self, self._sock.getsockname(), self.watson)
            self.logger.info(message)
        else:
            # ip が同じ
            message = ('{} client and watson use same IP. Therefore '
                       'don\'t send client.db to watson.').format(self)
            self.logger.info(message)

        for darkness_process in self.darkness_processes:
            self.total_created_nodes += \
                darkness_process.d_config['made_nodes'].value

        message = 'Client(id={}) created num of nodes {}'. \
                    format(self.id, self.total_created_nodes)
        self.logger.info(message)

    def _init_attrs(self):
        '''\
        watson に接続し、id, iso_start_up_timeを受信する。
        id は client.<id>.log として、log fileを作成するときに使用。
        start_up_time は db_dirを決定する際に使用する。
        '''
        d = self._hello_watson()
        if not d:
            self._sock.close()
            raise RuntimeError('client cannot say "I am Client." to watson who is {}'.format(self.watson))

        self.id = d['id']
        self.iso_start_up_time = d['iso_start_up_time']
        self.start_up_time = \
            isoformat_time_to_datetime(self.iso_start_up_time)
        self.log_level = d['log_level']
        self.db_dir = os.path.join(self.simulation_dir, \
            self.iso_start_up_time)
        self.client_db_path = os.path.join(self.db_dir,
                                     'client.{}.db'.format(self.id))
        self.node_index = d['node_index']
        self.schema_path = SCHEMA_PATH
        return d

    def _hello_watson(self):
        '''\
        watsonに "I am Client." をUDPで送信し、watson起動時刻(start_up_time)、
        watsonへの接続順位(=id)をUDPで受信する。
        この時、受信するのはjson文字列。
        simulation 結果を格納する db_dir を作成するための情報を得る。
        db_dir 以下には、client.id.log, client.id.db 等を作成する。

        3 回 watson へ "I am Client." と伝えようとしても駄目だった場合、
        空の dictionary を返す。
        dictionary を受け取る _init_attrs() では、RuntimeError()を上げる。
        '''
        tries = 0
        sheep = {}
        sheep['profess'] = 'I am Client.'
        sheep['num_nodes'] = self.num_nodes
        js = dict_becomes_jbytes(sheep)
        d = {}
        while tries < 3:
            try:
                self._sock.sendto(js, self.watson)
                recved_msg, who = self._sock.recvfrom(1024)
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
