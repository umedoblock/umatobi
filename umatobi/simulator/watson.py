import threading
import os
import sys
import socketserver
import datetime, time
import configparser
import sqlite3

from lib import make_logger, dict_becomes_jbytes, jtext_becomes_dict
from lib import make_start_up_orig, elapsed_time
from lib import SCHEMA_PATH, y15sformat_time
import simulator.sql

logger = None

# WatsonTCPOffice and WatsonOpenOffice classes are on different thread.
class WatsonOpenOffice(threading.Thread):
    def __init__(self, watson):
        threading.Thread.__init__(self)
        self.watson = watson
        self.in_serve_forever = threading.Event()
        thread_id = threading.get_ident()
        logger.debug(f"thread_id={thread_id} in WatsonOpenOffice.__init__()")

    def run(self):
        # Create the server, binding to localhost on port ???
        logger.debug(f"socketserver.TCPServer({self.watson.watson_office_addr}, WatsonOpenOffice)")
        with WatsonTCPOffice(self.watson) as watson_tcp_office:
            self.watson.watson_tcp_office = watson_tcp_office
            logger.debug("watson_open_office.serve_forever()")
            # WatsonOpenOffice() run on different thread of WatsonTCPOffice.
            self.in_serve_forever.set()
            self.watson.watson_office_addr_assigned.set()
            watson_tcp_office.serve_forever()

# WatsonTCPOffice and WatsonOffice classes are on same thread.
class WatsonTCPOffice(socketserver.TCPServer):
    def __init__(self, watson):
        thread_id = threading.get_ident()
        logger.debug(f"thread_id={thread_id} in WatsonTCPOffice.__init__()")
        ip, port = watson.watson_office_addr
        while True:
            addr = (ip, port)
            try:
                super().__init__(addr, WatsonOffice)
            except OSError as oe:
                if oe.errno != 98:
                    raise(oe)

              # [Errno 98] Address already in use
                port += 1
                if port > 65535:
                    raise RuntimeError("port number is over 65535")
                continue
            break

        # watson_office_addr が決定されている。
        watson.watson_office_addr = addr

        self.watson = watson
        self.clients = []
    #   self.server in WatsonOffice class means WatsonTCPOffice instance.
        self.start_up_orig = watson.start_up_orig
        self.simulation_db = simulator.sql.SQL(db_path=watson.simulation_db_path)
        self.simulation_db.access_db()

    def shutdown_request(self, request):
        pass

class WatsonOffice(socketserver.StreamRequestHandler):
    def handle(self):
        thread_id = threading.get_ident()
        logger.debug(f"thread_id={thread_id} in WatsonOffice.handle()")
        logger.debug("watson_office.handle()")
    #   self.server in WatsonOffice class means WatsonTCPOffice instance.
        logger.debug(f"WatsonOffice(request={self.request}, client_address={self.client_address}, server={self.server}")
        text_message = self.rfile.readline().strip()
        logger.debug(f"text_message = {text_message} in watson_office.handle()")

        sheep = jtext_becomes_dict(text_message)
        logger.debug(f"sheep = {sheep} in watson_office.handle()")
        professed = sheep['profess']
        num_nodes = sheep['num_nodes']

        logger.debug(f"self.server.start_up_orig={self.server.start_up_orig}")

        logger.debug(f"professed = {professed} in watson_office.handle()")
        logger.debug(f"type(self.server)={type(self.server)}")
        logger.debug(f"type(self)={type(self)}")
        logger.debug(f"dir(self)={dir(self)}")
        if professed == 'I am Client.':
            client_addr = self.client_address
            client_id = len(self.server.clients)
            self.server.clients.append(self)

            logger.info(f'Client(id={client_id}, ip:port={client_addr}) came here.')
            insert_clients = {
                'id': client_id,
                'host': client_addr[0],
                'port': client_addr[1],
                'joined': elapsed_time(self.server.start_up_orig),
                'num_nodes': num_nodes,
            }
            sql = self.server.simulation_db.insert('clients', insert_clients)
            logger.debug(f"simulation_db.insert({sql})")
            self.server.simulation_db.commit()
            logger.debug('{} {}'.format(self, sql))
            logger.debug('{} recved={}'.format(self, insert_clients))

            to_client = {
                'dir_name': self.server.watson.dir_name,
                'client_id': client_id,
                'start_up_time': y15sformat_time(self.server.start_up_orig),
                'node_index': self.server.watson.total_nodes,
                'log_level': self.server.watson.log_level,
            }
            self.server.watson.total_nodes += num_nodes
            logger.info(f'watson.total_nodes={self.server.watson.total_nodes}, Client(id={client_id}).')
            reply = dict_becomes_jbytes(to_client)
        else:
            logger.info(f'unknown professed = "{professed}" in watson_office.handle()')
            reply = b'Go back home.'

        logger.info(f'watson send to_client={reply}) to Client(id={client_id}).')
        self.wfile.write(reply)

    def finish(self):
        pass

    def bye_bye(self):
        super().finish()

class Watson(threading.Thread):
    MAX_NODE_NUM=8

    def __init__(self, watson_office_addr, simulation_seconds, start_up_orig, dir_name, log_level):
        '''\
        watson: Cient, Node からの TCP 接続を待つ。
        起動時刻を start_up_time と名付けて記録する。
        '''
        threading.Thread.__init__(self)

        global logger
        if not logger:
            logger = make_logger(dir_name, name="watson", level=log_level)
        thread_id = threading.get_ident()
        logger.debug("debuging...")
        logger.info(f"thread_id={thread_id} in Watson.__init__()")
        self.log_level = log_level

        self.watson_office_addr = watson_office_addr
        self.watson_office_addr_assigned = threading.Event()
        self.simulation_seconds = simulation_seconds
        self.log_level = log_level
        self.dir_name = dir_name
        self.registered_nodes = 0

        self.start_up_orig = start_up_orig
        self.start_up_time = y15sformat_time(self.start_up_orig)

        self.simulation_db_path = os.path.join(self.dir_name, 'simulation.db')
        self.schema_path = SCHEMA_PATH

        self.timeout_sec = 1
        self.nodes = []
        self.total_nodes = 0

        self._make_office()

    def _make_office(self):
        '''watson が書き出す log 用の directory 作成'''
        os.makedirs(self.dir_name, exist_ok=True)

        logger.info('----- watson office start up. -----')
        message = 'simulation_seconds={}'.format(self.simulation_seconds)
        logger.info(message)

    def run(self):
        '''simulation 開始'''
        self.simulation_db = simulator.sql.SQL(
                                db_path=self.simulation_db_path,
                                schema_path=self.schema_path)
        self.simulation_db.create_db()
        self.simulation_db.create_table('clients')
        # この後，WatsonTCPOffice が simulation_db に access する。
        # sqlite3 では， sqlite3.connect(self.db_path) の返す instance を
        # 作成した thread と別の thread では使えないので，一度閉じている。
        self.simulation_db.close()
        logger.debug("watson created clients table.")

        watson_open_office = WatsonOpenOffice(self)
        self.watson_open_office = watson_open_office
        logger.debug("watson_open_office.start()")
        watson_open_office.start()
        # wait a minute
        # to set watson_open_office instance
        # to watson instance
        # in WatsonOpenOffice.run()
        watson_open_office.in_serve_forever.wait()
        # watson.watson_office_addr が決定している。

        while elapsed_time(self.start_up_orig) < self.simulation_seconds * 1000:
            logger.debug("watson time.sleep(1.0)")
            time.sleep(1.0)

        self._release_clients()

        # close watson office
        self.watson_tcp_office.shutdown()

      # self._wait_tcp_clients()
        self._wait_client_db()

        # simulation_db に骨格を作成する。
        # simulation も終わるってのにねぇ。
        self.simulation_db.access_db()
        self._merge_db_to_simulation_db()
        self._construct_simulation_table()
        self.simulation_db.close()

    def _construct_simulation_table(self):
        self.simulation_db.create_table('simulation')
        d_simulation = {}
        d_simulation['watson_office_addr'] = '{}:{}'.format(*self.watson_office_addr)
        d_simulation['simulation_milliseconds'] = \
            1000 * self.simulation_seconds
        d_simulation['title'] = 'umatobi-simulation'
        d_simulation['memo'] = 'なにかあれば'
        d_simulation['total_nodes'] = self.total_nodes
        d_simulation['n_clients'] = len(self.watson_tcp_office.clients)
        d_simulation['version'] = '0.0.0'
        self.simulation_db.insert('simulation', d_simulation)
        self.simulation_db.commit()

    def _wait_client_db(self):
        logger.info('{} は、client.#.dbの回収に乗り出した。'.format(self))
        logger.info('{} なんて言いながら実は待機してるだけ。'.format(self))
        logger.info('{} client.{}.dbの回収完了。'.format(self, 1))

    def _merge_db_to_simulation_db(self):
        logger.info('{} client.#.db の結合開始。'.format(self))
        logger.info('{} client.#.db の結合終了。'.format(self))

    def join(self):
        '''watson threadがjoin'''
        threading.Thread.join(self)
        logger.debug('watson thread joined.')

    def _tcp_office_open(self):
        _wait_tcp_clients()

    def _release_clients(self):
        '''\
        watsonが把握しているClientに "break down" を送信し、
        各Clientに終了処理を行わせる。
        Clientは、終了処理中に client.id.db を送信してくる。
        '''
        logger.debug('watson._release_clients()')
        for watson_office_client in self.watson_tcp_office.clients:
            result = b'break down.'
            logger.debug(f"type(watson_office_client)={type(watson_office_client)} in _release_clients()")
            logger.debug(f"watson_office_client={watson_office_client} in _release_clients()")
            logger.debug(f"watson_office_client.request={watson_office_client.request} in _release_clients()")
            watson_office_client.wfile.write(result)
            watson_office_client.bye_bye()

    def __str__(self):
        return 'Watson({}:{})'.format(*self.watson_office_addr)
