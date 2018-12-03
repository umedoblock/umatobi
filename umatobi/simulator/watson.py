import threading
import os
import sys
import socketserver
import datetime, time
import configparser
import sqlite3

from lib import make_logger, dict_becomes_jbytes, jbytes_becomes_dict
from lib import make_start_up_orig, elapsed_time
from lib import SCHEMA_PATH
import simulator.sql

logger = None

#  class socketserver.\
#        TCPServer(server_address, RequestHandlerClass, bind_and_activate=True)
class WatsonTCPOffice(socketserver.TCPServer):
    def __init__(self, office_addr, RequestHandlerClass, start_up_orig, watson_db):
        thread_id = threading.get_ident()
        logger.info(f"thread_id={thread_id} in WatsonTCPOffice.__init__()")
        super().__init__(office_addr, RequestHandlerClass)
        self.start_up_orig = start_up_orig
        self.watson_db = watson_db

class WatsonOpenOffice(threading.Thread):
    def __init__(self, office_addr, start_up_orig, watson_db_path):
        threading.Thread.__init__(self)
        thread_id = threading.get_ident()
        logger.info(f"thread_id={thread_id} in WatsonOpenOffice.__init__()")
        self.office_addr = office_addr
        self.start_up_orig = start_up_orig
        self.watson_db_path = watson_db_path
        self.watson_db = simulator.sql.SQL(owner=self,
                                           db_path=watson_db_path)
        self.watson_db.access_db()

    def run(self):
        # Create the server, binding to localhost on port ???
        logger.info(f"socketserver.TCPServer({self.office_addr}, WatsonOpenOffice)")
        with WatsonTCPOffice(self.office_addr, WatsonOffice, self.start_up_orig, self.watson_db) as watson_tcp_office:
            logger.info("watson_open_office.serve_forever()")
            watson_tcp_office.serve_forever()
#       with socketserver.TCPServer(self.office, WatsonOffice) as watson_office:
#           logger.info("watson_open_office.serve_forever()")
#           watson_office.start_up_time = self.start_up_time
#           watson_office.serve_forever()


class WatsonOffice(socketserver.StreamRequestHandler):
#class BaseRequestHandler:
#####def __init__(self, request, client_address, server):
#####    self.request = request
#####    self.client_address = client_address
#####    self.server = server
#####    self.setup()
#####    try:
#####        self.handle()
#####    finally:
#####        self.finish()

#####def setup(self):
#####    pass

#####def handle(self):
#####    pass

#####def finish(self):
#####    pass

####class StreamRequestHandler(BaseRequestHandler):
####    rbufsize = -1
####    wbufsize = 0
####
####    # A timeout to apply to the request socket, if not None.
####    timeout = None
####
####    # Disable nagle algorithm for this socket, if True.
####    # Use only when wbufsize != 0, to avoid small packets.
####    disable_nagle_algorithm = False
####
####    def setup(self):
####        self.connection = self.request
####        if self.timeout is not None:
####            self.connection.settimeout(self.timeout)
####        if self.disable_nagle_algorithm:
####            self.connection.setsockopt(socket.IPPROTO_TCP,
####                                       socket.TCP_NODELAY, True)
####        self.rfile = self.connection.makefile('rb', self.rbufsize)
####        self.wfile = self.connection.makefile('wb', self.wbufsize)
####
####    def finish(self):
####        if not self.wfile.closed:
####            self.wfile.flush()
####        self.wfile.close()
####        self.rfile.close()

    def handle(self):
        thread_id = threading.get_ident()
        logger.info(f"thread_id={thread_id} in WatsonOffice.handle()")
        logger.info("watson_office.handle()")
        logger.info(f"WatsonOffice(request={self.request}, client_address={self.client_address}, server={self.server}")
        text_message = self.rfile.readline().strip()
        logger.info(f"text_message = {text_message} in watson_office.handle()")

        sheep = jbytes_becomes_dict(text_message)
        logger.info(f"sheep = {sheep} in watson_office.handle()")
        professed = sheep['profess']
        num_nodes = sheep['num_nodes']

        logger.info(f"self.server.start_up_orig={self.server.start_up_orig}")

        logger.info(f"professed = {professed} in watson_office.handle()")
        logger.info(f"type(self.server)={type(self.server)}")
        logger.info(f"type(self)={type(self)}")
        logger.info(f"dir(self)={dir(self)}")
        if professed == 'I am Client.':
            client_addr = self.client_address
            client_id = 0

            logger.info('{} Client(client_id=0, ip:port={}) came here.'.format(self, client_addr))
            d = {}
            d['client_id'] = client_id
            d['host'] = client_addr[0]
            d['port'] = client_addr[1]
            d['joined'] = elapsed_time(self.server.start_up_orig)
            d['num_nodes'] = num_nodes
            sql = self.server.watson_db.insert('clients', d)
            logger.info(f"watson_db.insert({sql})")
            self.server.watson_db.commit()
            logger.debug('{} {}'.format(self, sql))
            logger.info('{} recved={}'.format(self, d))

            d.clear()
            d['id'] = 0
            d['start_up_time'] = self.start_up_time
            d['node_index'] = 1 + self.registered_nodes
            self.registered_nodes += num_nodes
            self.total_nodes += num_nodes
            reply = dict_becomes_jbytes(d)
            count_clients += 1
        else:
            logger.debug('crazy man.')
            logger.info(f'unknown professed = "{professed}" in watson_office.handle()')
            reply = b'Go back home.'

        self.wfile.write(reply)
        count_inquiries += 1
        self.server.tcp_clients.append(self)

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
        logger.info(f"thread_id={thread_id} in Watson.__init__()")

        self.watson_office_addr = watson_office_addr
        self.simulation_seconds = simulation_seconds
        self.log_level = log_level
        self.dir_name = dir_name
        self.registered_nodes = 0
        self.watson_db = None # sql.SQL()

        self.start_up_orig = start_up_orig
        self.start_up_time = self.start_up_orig.isoformat()

        self.simulation_db_path = os.path.join(self.dir_name, 'simulation.db')
        self.watson_db_path = os.path.join(self.dir_name, 'watson.db')
        self.schema_path = SCHEMA_PATH

        self.timeout_sec = 1
        self.nodes = []
        self.total_nodes = 0
        self.clients = []

        self._make_office()

    def _make_office(self):
        '''watson が書き出す log 用の directory 作成'''
        os.makedirs(self.dir_name, exist_ok=True)

        logger.info('----- watson office start up. -----')
        message = 'simulation_seconds={}'.format(self.simulation_seconds)
        logger.info(message)

    def run(self):
        '''simulation 開始'''
        self.watson_db = simulator.sql.SQL(owner=self,
                                     db_path=self.watson_db_path,
                                     schema_path=self.schema_path)
        self.watson_db.create_db()
        self.watson_db.create_table('clients')
        logger.info("watson created clients table.")

        watson_open_office = WatsonOpenOffice(self.watson_office_addr, self.start_up_orig, self.watson_db_path)
        logger.info("watson_open_office.start()")
        watson_open_office.start()

        while elapsed_time(self.start_up_orig) < self.simulation_seconds * 1000:
            logger.info("watson time.sleep(1.0)")
            time.sleep(1.0)

        self._release_clients()

        # close watson office
        watson_open_office.shutdown()

      # self._wait_tcp_clients()
        self._wait_client_db()
        self._merge_db_to_simulation_db()
        self._construct_simulation_table()
        self.watson_db.close()

    def _construct_simulation_table(self):
        self.watson_db.create_table('simulation')
        d_simulation = {}
        d_simulation['watson_office_addr'] = '{}:{}'.format(*self.watson_office_addr)
        d_simulation['simulation_milliseconds'] = \
            1000 * self.simulation_seconds
        d_simulation['title'] = 'umatobi-simulation'
        d_simulation['memo'] = 'なにかあれば'
        d_simulation['total_nodes'] = self.total_nodes
        d_simulation['n_clients'] = len(self.clients)
        d_simulation['version'] = '0.0.0'
        self.watson_db.insert('simulation', d_simulation)
        self.watson_db.commit()

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
        self._tcp_sock.close()
        logger.info('watson thread joined.')

    def _tcp_office_open(self):
        _wait_tcp_clients()

    def _wait_tcp_clients(self):
        '''\
        Client, Node からの接続を待つ。
        "I am Client." を受信したら、Clientからの接続と判断する。
        そして、start_up_time, 接続順位を json string にして返す。
        "I am Node." を受信したら、Nodeからの接続と判断する。
        まだ未定。
        '''
        count_inquiries = 0
        count_clients = 1

        while elapsed_time(self) < self.simulation_seconds * 1000:
          # logger.info('passed time {:.3f}'.format(self.passed_time()))

            try:
              # print('================= count_inquiries =', count_inquiries)
              # print('self._sock.recvfrom() ==============================')
                self.rdata = self.rfile.readline().strip()
                text_message, phone_number = self._tcp_sock.recvfrom(1024)
            except socket.timeout:
              # print('phone_number timeouted.')
                phone_number = None

            if not phone_number:
                continue
            sheep = jbytes_becomes_dict(text_message)
            professed = sheep['profess']
            num_nodes = sheep['num_nodes']

            if professed == 'I am Node.':
                csv = self.collect_nodes_as_csv()
                logger.info('realizing_nodes = "{}"'.format(csv))
                realizing_nodes = csv.encode()

                self.nodes.append(phone_number)
                if len(self.nodes) > self.MAX_NODE_NUM:
                    survived_node_index = len(self.nodes) - self.MAX_NODE_NUM
                    self.nodes = self.nodes[survived_node_index:]

                reply = realizing_nodes
            elif professed == 'I am Client.':
                id = count_clients
                self.clients.append(phone_number)
                logger.info('{} Client(id={}, ip:port={}) came here.'.format(self, id, phone_number))

                d = {}
                d['id'] = id
                d['host'] = phone_number[0]
                d['port'] = phone_number[1]
                d['joined'] = elapsed_time(self)
                d['log_level'] = self.log_level
                d['num_nodes'] = num_nodes
                sql = self.watson_db.insert('clients', d)
                self.watson_db.commit()
                logger.debug('{} {}'.format(self, sql))
                logger.info('{} recved={}'.format(self, d))

                d.clear()
                d['id'] = id
                d['start_up_time'] = self.start_up_time
                d['log_level'] = self.log_level
                d['node_index'] = 1 + self.registered_nodes
                self.registered_nodes += num_nodes
                self.total_nodes += num_nodes
                reply = dict_becomes_jbytes(d)
                count_clients += 1
            else:
                logger.debug('crazy man.')
                reply = b'Go back home.'

            self._tcp_sock.send(reply, phone_number)
            count_inquiries += 1

    def _release_clients(self):
        '''\
        watsonが把握しているClientに "break down" を送信し、
        各Clientに終了処理を行わせる。
        Clientは、終了処理中に client.id.db を送信してくる。
        '''
        logger.info('watson._release_clients()')
        for client in self.clients:
            result = b'break down.'
            self._tcp_sock.send(result, client)
            self.wfile.write(result)

    def collect_nodes_as_csv(self):
        '''watsonが把握しているnodeのaddressをcsv化する。'''
        csv = ','.join(['{}:{}'.format(*node) for node in self.nodes])
        return csv

    def __str__(self):
        return 'Watson({}:{})'.format(*self.watson_office_addr)
