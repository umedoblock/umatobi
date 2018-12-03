import sys, os
import threading
import sqlite3
import socket
import multiprocessing

from simulator.darkness import Darkness
import simulator.sql
from lib import make_logger, jtext_becomes_dict, dict_becomes_jbytes
from lib import SCHEMA_PATH, isoformat_time_to_datetime

logger = None

def make_darkness(d_config):
    '''darkness process を作成'''
    darkness_ = Darkness(**d_config)
    darkness_.start()

class Client(object):
    NODES_PER_DARKNESS = 4

    def __init__(self, watson_office_addr, num_nodes):
        '''\
        Clientは各PCに付き一つ作成する。
        dir_name 以下に，Client が作成する一切合財を保存する。
        '''

        global logger
        if not logger:
            logger = make_logger(".", name="client", level='INFO')

        if isinstance(num_nodes, int) and num_nodes > 0:
            pass
        else:
            raise RuntimeError('num_nodes must be positive integer.')

        self.watson_office_addr = watson_office_addr # (IP, PORT)
        logger.info(f"self.watson_office_addr={self.watson_office_addr}")
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
        self._tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        logger.info(f"self._tcp_sock.connect(={watson_office_addr})")
        self._tcp_sock.connect(watson_office_addr)
        _d_init_attrs = self._init_attrs()
        logger = make_logger(self.dir_name, name="client", level=self.log_level)

        logger.info('----- {} log start -----'.format(self))
        logger.info('watson_office_addr = {}'.format(self.watson_office_addr))
        logger.info('   dir_name = {}'.format(self.dir_name))
        logger.info('client_db_path = {}'.format(self.client_db_path))
        logger.info('----- client.{} initilized end -----'.
                          format(self.id))
        logger.debug('{} d={}'.format(self, _d_init_attrs))
        logger.debug('{} node_index={}'.format(self, self.node_index))
        logger.debug('{} debug log test.'.format(self))
        logger.info('')

    def start(self):
        '''\
        Darknessを、たくさん作成する。
        作成後は、watsonから終了通知("break down")を受信するまで待機する。
        '''
        logger.info('Client(id={}) started!'.format(self.id))
        self.client_db = simulator.sql.SQL(db_path=self.client_db_path,
                                           schema_path=self.schema_path)
        self.client_db.create_db()
        logger.info('{} client_db.create_db().'.format(self))
        self.client_db.create_table('growings')
        logger.info('{} client_db.create_table(\'growings\').'.format(self))

        # Darkness が作成する node の数を設定する。
        nodes_per_darkness = self.nodes_per_darkness

        # for 内で darkness_process を作成し、
        # 順に darkness_processes に追加していく。
        for darkness_id in range(0, self.num_darkness):
            first_node_id = self.node_index + \
                            darkness_id * self.nodes_per_darkness
            if darkness_id == self.num_darkness:
                # 最後に端数を作成？
                nodes_per_darkness = self.last_darkness_make_nodes
            logger.info('darkness id={}, nodes_per_darkness={}'.format(darkness_id, nodes_per_darkness))
            client_id = self.id

            # client と darkness process が DarknessConfig を介して通信する。
            darkness_d_config = {
                'dir_name':  self.dir_name, 'id':  darkness_id,
                'client_id':  client_id,
                'log_level':  self.log_level,
                'start_up_time':  self.start_up_time,
                'first_node_id':  first_node_id,
                'num_nodes':  nodes_per_darkness,
                # share with client and darknesses
                'made_nodes':  multiprocessing.Value('i', 0),
                # share with client and another darknesses
                'leave_there':  self.leave_there,
            }
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
            logger.debug(f'self._tcp_sock={self._tcp_sock} in Client.start()')
            try:
                recved_msg = self._tcp_sock.recv(1024)
            except socket.timeout:
                recved = b''
                continue

            if recved_msg == b'break down.':
                logger.info('Client(id={}) got break down from {}.'.format(self.id, recved_msg))
                break

        # Client 終了処理開始。
        self._release()

        self._tcp_sock.shutdown(socket.SHUT_WR)

    def join(self):
        '''threading.Thread を使用していた頃の名残。'''
        logger.info('Client(id={}) thread joined.'.format(self.id))

    def _release(self):
        '''\
        Client 終了処理。leave_thereにsignal を set することで、
        Clientの作成した Darkness達は一斉に終了処理を始める。
        '''
        logger.info(('Client(id={}) set signal to leave_there '
                          'for Darknesses.').format(self.id))
        self.leave_there.set()

        for darkness_p in self.darkness_processes:
            darkness_p.join()
            msg = 'Client(id={}), Darkness(id={}) process joined.'. \
                   format(self.id, darkness_p.d_config['id'])
            logger.info(msg)
        logger.info('Client(id={}) thread released.'.format(self.id))

        self.client_db.close()
        logger.info('{} client_db.close().'.format(self))
      # logger.error('self._sock.getsockname() =', ('127.0.0.1', 20000))
        # ip のみ比較、 compare only ip
        if False and self._tcp_sock.getsockname()[0] != self.watson_office_addr[0]:
            logger.error('TODO: #169 simulation終了後、clientがclient.1.dbをwatsonにTCPにて送信。')
            # _sock=('0.0.0.0', 22343), watson_office_addr=('localhost', 55555)
            message = '{} _sock={}, watson_office_addr={}'. \
                       format(self, self._tcp_sock.getsockname(), self.watson_office_addr)
            logger.info(message)
        else:
            # ip が同じ
            message = ('{} client and watson use same IP. Therefore '
                       'don\'t send client.db to watson.').format(self)
            logger.info(message)

        for darkness_process in self.darkness_processes:
            self.total_created_nodes += \
                darkness_process.d_config['made_nodes'].value

        message = 'Client(id={}) created num of nodes {}'. \
                    format(self.id, self.total_created_nodes)
        logger.info(message)

    def _init_attrs(self):
        '''\
        watson に接続し、id, iso_start_up_timeを受信する。
        id は client.<id>.log として、log fileを作成するときに使用。
        start_up_time は dir_nameを決定する際に使用する。
        '''
        d = self._hello_watson()
        logger.debug(f"_hello_watson() return d={d} in Client._init_attrs()")
        if not d:
            self._tcp_sock.close()
            raise RuntimeError('client cannot say "I am Client." to watson where is {}'.format(self.watson_office_addr))

        self.id = d['client_id']
        self.start_up_time = d['start_up_time']
        self.dir_name = d['dir_name']
        self.client_db_path = os.path.join(self.dir_name,
                                     'client.{}.db'.format(self.id))
        self.node_index = d['node_index']
        self.log_level = d['log_level']
        self.schema_path = SCHEMA_PATH
        return d

    def _hello_watson(self):
        '''\
        watsonに "I am Client." をTCPで送信し、watson起動時刻(start_up_time)、
        watsonへの接続順位(=id)をTCPで受信する。
        この時、受信するのはjson文字列。
        simulation 結果を格納する dir_name を作成するための情報を得る。
        dir_name 以下には、client.id.log, client.id.db 等を作成する。

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
            logger.debug(f"js={js}")
            try:
                self._tcp_sock.sendall(js)
            except socket.timeout as e:
                logger.debug(f"{str(self)} was timeout by send(), tries={tries}")
                tries += 1
                continue
            logger.debug(f"send js={js} in _hello_watson()")
            break

        if tries >= 3:
            raise RuntimeError(f"cannot send js={js}")

        tries = 0
        while tries < 3:
            try:
                recved_msg = self._tcp_sock.recv(1024)
            except socket.timeout as e:
                logger.debug(f"{str(self)} was timeout by recv(), tries={tries}")
                tries += 1
                continue
          # if self.watson == who:
            logger.debug(f"recved_msg={recved_msg}")
            jt = recved_msg.decode("utf-8")
            d = jtext_becomes_dict(jt)
            break

      # print('who =', file=sys.stderr)
      # print(who, file=sys.stderr)
      # print('d =', file=sys.stderr)
      # print(d, file=sys.stderr)

        return d

    def __str__(self):
        return 'Client(id={})'.format(self.id)
