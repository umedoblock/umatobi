import sys, os
import threading
import sqlite3
import socket
import multiprocessing
from logging import StreamHandler

from umatobi.log import *
from umatobi.constants import *
from umatobi.simulator.darkness import Darkness
from umatobi import simulator
from umatobi.lib import json2dict, dict2json, dict2bytes, bytes2dict

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

        logger.info(f"Client(self={self}, watson_office_addr={watson_office_addr}, num_nodes={num_nodes})")

        if isinstance(num_nodes, int) and num_nodes > 0:
            pass
        else:
            raise RuntimeError('num_nodes must be positive integer.')

        self.watson_office_addr = watson_office_addr # (IP, PORT)
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

        self.leave_there = multiprocessing.Event()

        self.timeout_sec = 1
        socket.setdefaulttimeout(self.timeout_sec)

    def consult_watson(self):
        logger.info(f"{self}.consult_watson()")
        self._tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        logger.info(f"{self}.consult_watson(), _tcp_sock.connect(={self.watson_office_addr})")
        self._tcp_sock.connect(self.watson_office_addr)

        _d_init_attrs = self._init_attrs()

        client_id = self.id

    def start(self):
        '''\
        Darknessを、たくさん作成する。
        作成後は、watsonから終了通知("break down")を受信するまで待機する。
        '''
        logger.info(f"{self}.start()")

        self.consult_watson()

        self._make_growings_table()

        self._start_darkness()

        self._wait_break_down()

        # Client 終了処理開始。
        self._release()
        self.close()

    def close(self):
        # must be close() not shutdown() about socket.SOCK_STREAM
        # ResourceWarning: unclosed <socket.socket fd=7, ...
        logger.info(f"{self}.close()")
        self._tcp_sock.close()

    def _make_growings_table(self):
        logger.info(f"{self}._make_growings_table()")
        self.client_db = simulator.sql.SQL(db_path=self.client_db_path,
                                           schema_path=self.schema_path)
        self.client_db.create_db()
        self.client_db.create_table('growings')

    def _start_darkness(self):
        logger.info(f"{self}._start_darkness()")
        # Darkness が作成する node の数を設定する。
        nodes_per_darkness = self.nodes_per_darkness

        # for 内で darkness_process を作成し、
        # 順に darkness_processes に追加していく。
        for darkness_id in range(0, self.num_darkness):
            first_node_id = self.node_index + \
                            darkness_id * self.nodes_per_darkness
            if darkness_id == self.num_darkness - 1:
                # 最後に端数を作成？
                nodes_per_darkness = self.last_darkness_make_nodes
            logger.info(f"client_id={self.id}, darkness id={darkness_id}, num_darkness={self.num_darkness}, num_nodes={nodes_per_darkness}, first_node_id={first_node_id}")
            client_id = self.id

            # client と darkness process が DarknessConfig を介して通信する。
            darkness_d_config = {
                'id':  darkness_id,
                'client_id':  client_id,
                'start_up_time':  self.start_up_time,
                'dir_name':  self.dir_name,
                'log_level':  self.log_level,
                'num_nodes':  nodes_per_darkness,
                'first_node_id':  first_node_id,
                'num_darkness': self.num_darkness,
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
            self.darkness_processes.append(darkness_process)

        for darkness_process in self.darkness_processes:
            darkness_process.start()

    def _wait_break_down(self):
        logger.info(f"{self}._wait_break_down()")
        # watson から終了通知("break down")が届くまで待機し続ける。
        # TODO: #149 watson からの接続であると確認する。
        while True:
            logger.debug(f"{self}._wait_break_down(), _tcp_sock={self._tcp_sock}")
            try:
                recved_msg = self._tcp_sock.recv(1024)
            except socket.timeout:
                recved = b''
                continue

            if recved_msg == b'break down.':
                logger.info(f"{self}._wait_break_down(), {self} got break down from {self._tcp_sock}.")
                break

    def join(self):
        '''threading.Thread を使用していた頃の名残。'''
        logger.info(f"{self}.join()")

    def _release(self):
        '''\
        Client 終了処理。leave_thereにsignal を set することで、
        Clientの作成した Darkness達は一斉に終了処理を始める。
        '''
        logger.info(f"{self}._release()")
        self.leave_there.set()

        for darkness_p in self.darkness_processes:
            darkness_p.join()
            logger.info(f"{self}._release(), {darkness_p} process joind.")

        logger.info(f"{self.client_db}.close()")
        self.client_db.close()
      # logger.error('self._sock.getsockname() =', ('127.0.0.1', 20000))
        # ip のみ比較、 compare only ip
        if False and self._tcp_sock.getsockname()[0] != self.watson_office_addr[0]:
            logger.error('TODO: #169 simulation終了後、clientがclient.N.dbをwatsonにTCPにて送信。')
            # _sock=('0.0.0.0', 22343), watson_office_addr=('localhost', 55555)
            logger.info(f"{self}._release(), {self} got break down from watson(={self.watson}). send client.{client.id}.db to {self._tcp_sock}.")
        else:
            # ip が同じ
            message = (f"{self}._release(), client and watson use same IP. " +
                       f"Therefore " +
                       f"don\'t send client.{self.id}.db to watson.")
            logger.info(message)

        for darkness_process in self.darkness_processes:
            self.total_created_nodes += \
                darkness_process.d_config['made_nodes'].value

        logger.info(f"{self} created num of nodes {self.total_created_nodes}")

    def _init_attrs(self):
        '''\
        watson に接続し、id, start_up_timeを受信する。
        id は client.N.log として、log fileを作成するときに使用。
        start_up_time は dir_nameを決定する際に使用する。
        '''
        logger.info(f"{self}._hello_watson()")
        d = self._hello_watson()
      # logger.debug(f"_hello_watson() return d={d} in Client._init_attrs()")
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
        dir_name 以下には、client.N.log, client.N.db 等を作成する。

        3 回 watson へ "I am Client." と伝えようとしても駄目だった場合、
        空の dictionary を返す。
        dictionary を受け取る _init_attrs() では、RuntimeError()を上げる。
        '''
        tries = 0
        sheep = {}
        sheep['profess'] = 'I am Client.'
        sheep['num_nodes'] = self.num_nodes
        j = dict2json(sheep)
        b = dict2bytes(sheep)
        logger.info(f"{self}._hello_watson(), sheep={sheep}, j={j}")
        d = {}
        while tries < 3:
            logger.info(f"{self}._hello_watson(), {self._tcp_sock}.sendall(j={j}), tries={tries}.")
            try:
                self._tcp_sock.sendall(b)
                break
            except socket.timeout as e:
                logger.info(f"{self}._hello_watson(), {self._tcp_sock} timout by.")
                tries += 1
                continue

        if tries >= 3:
            raise RuntimeError(f"cannot send j={j} to addr={self.watson_office_addr}")
      # self._tcp_sock.shutdown(socket.SHUT_WR)

        tries = 0
        recved_msg = b'<empty>'
        while tries < 3:
            logger.info(f"{self}._hello_watson(), {self._tcp_sock}.recv(1024), tries={tries}")
            try:
                recved_msg = self._tcp_sock.recv(1024)
                break
            except socket.timeout as e:
                logger.info(f"{self}._hello_watson(), {self._tcp_sock} timout by recv(1024), tries={tries}.")
                tries += 1
                continue
        logger.debug(f"{self}._hello_watson(), recved_msg={recved_msg}, tries={tries}.")
        d = bytes2dict(recved_msg)
      # print("recved_msg =")
      # print(recved_msg)
      # text = recved_msg.decode()
      # logger.debug(f"{self}._hello_watson(), recved_msg.decode('utf-8')={text}, tries={tries}.")
      # d = json2dict(text)

        logger.debug(f"{self}._hello_watson(), d={d}, tries={tries}.")

        return d
