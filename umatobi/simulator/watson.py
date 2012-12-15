import threading
import os
import sys
import socket
import datetime
import configparser
import sqlite3

from lib import make_logger, dict_becomes_jbytes, jbytes_becomes_dict
from lib import make_start_up_time, elapsed_time
from lib import set_logging_startTime_from_start_up_time
from lib import SCHEMA_PATH
import simulator.sql

class Watson(threading.Thread):
    MAX_NODE_NUM=8

    def __init__(self, office, simulation_seconds, simulation_dir, log_level):
        '''\
        watson: Cient, Node からの UDP 接続を待つ。
        起動時刻を start_up_time と名付けて記録する。
        simulation_dir 以下に起動時刻を元にした db_dir を作成する。
        db_dir 以下に、simulation結果の生成物、
        simulation.db, watson.0.log, client.0.log ...
        を作成する。
        '''
        threading.Thread.__init__(self)
        self.office = office
        self.simulation_seconds = simulation_seconds
        self.log_level = log_level
        self.registered_nodes = 0
        self.watson_db = None # sql.SQL()

        self.start_up_time = make_start_up_time()
        self.iso_start_up_time = self.start_up_time.isoformat()
        set_logging_startTime_from_start_up_time(self)

        self.simulation_dir = simulation_dir
        self.db_dir = \
            os.path.join(self.simulation_dir, self.iso_start_up_time)
        self.simulation_db_path = os.path.join(self.db_dir, 'simulation.db')
        self.watson_db_path = os.path.join(self.db_dir, 'watson.db')
        self.schema_path = SCHEMA_PATH

        self.timeout_sec = 1
        self.nodes = []
        self.total_nodes = 0
        self.clients = []

        # socket() must set under setdefaulttimeout()
        socket.setdefaulttimeout(self.timeout_sec)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._sock.bind(self.office)

        self._make_office()

    def _make_office(self):
        '''watson が書き出す log 用の directory 作成'''
        os.makedirs(self.db_dir)

        self.logger = make_logger(self.db_dir, 'watson', level=self.log_level)
        self.logger.info('----- watson office start up. -----')
        message = 'simulation_seconds={}'.format(self.simulation_seconds)
        self.logger.info(message)

    def run(self):
        '''simulation 開始'''
        self.watson_db = simulator.sql.SQL(owner=self,
                                     db_path=self.watson_db_path,
                                     schema_path=self.schema_path)
        self.watson_db.create_db()
        self.watson_db.create_table('clients')

        self._wait_clients()
        self._release_clients()
        self._wait_client_db()
        self._merge_db_to_simulation_db()
        self._construct_simulation_table()
        self.watson_db.close()

    def _construct_simulation_table(self):
        self.watson_db.create_table('simulation')
        d_simulation = {}
        d_simulation['watson_office'] = '{}:{}'.format(*self.office)
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
        self.logger.info('{} は、client.#.dbの回収に乗り出した。'.format(self))
        self.logger.info('{} なんて言いながら実は待機してるだけ。'.format(self))
        self.logger.info('{} client.{}.dbの回収完了。'.format(self, 1))

    def _merge_db_to_simulation_db(self):
        self.logger.info('{} client.#.db の結合開始。'.format(self))
        self.logger.info('{} client.#.db の結合終了。'.format(self))

    def join(self):
        '''watson threadがjoin'''
        threading.Thread.join(self)
        self._sock.close()
        self.logger.info('watson thread joined.')

    def _wait_clients(self):
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
          # self.logger.info('passed time {:.3f}'.format(self.passed_time()))

            try:
              # print('================= count_inquiries =', count_inquiries)
              # print('self._sock.recvfrom() ==============================')
                text_message, phone_number = self._sock.recvfrom(1024)
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
                self.logger.info('realizing_nodes = "{}"'.format(csv))
                realizing_nodes = csv.encode()

                self.nodes.append(phone_number)
                if len(self.nodes) > self.MAX_NODE_NUM:
                    survived_node_index = len(self.nodes) - self.MAX_NODE_NUM
                    self.nodes = self.nodes[survived_node_index:]

                reply = realizing_nodes
            elif professed == 'I am Client.':
                id = count_clients
                self.clients.append(phone_number)
                self.logger.info('{} Client(id={}, ip:port={}) came here.'.format(self, id, phone_number))

                d = {}
                d['id'] = id
                d['host'] = phone_number[0]
                d['port'] = phone_number[1]
                d['joined'] = elapsed_time(self)
                d['log_level'] = self.log_level
                d['num_nodes'] = num_nodes
                sql = self.watson_db.insert('clients', d)
                self.watson_db.commit()
                self.logger.debug('{} {}'.format(self, sql))
                self.logger.info('{} recved={}'.format(self, d))

                d.clear()
                d['id'] = id
                d['iso_start_up_time'] = self.iso_start_up_time
                d['log_level'] = self.log_level
                d['node_index'] = 1 + self.registered_nodes
                self.registered_nodes += num_nodes
                self.total_nodes += num_nodes
                reply = dict_becomes_jbytes(d)
                count_clients += 1
            else:
                self.logger.debug('crazy man.')
                reply = b'Go back home.'

            self._sock.sendto(reply, phone_number)
            count_inquiries += 1

    def _release_clients(self):
        '''\
        watsonが把握しているClientに "break down" を送信し、
        各Clientに終了処理を行わせる。
        Clientは、終了処理中に client.id.db を送信してくる。
        '''
        self.logger.info('watson._release_clients()')
        for client in self.clients:
            result = b'break down.'
            self._sock.sendto(result, client)

    def collect_nodes_as_csv(self):
        '''watsonが把握しているnodeのaddressをcsv化する。'''
        csv = ','.join(['{}:{}'.format(*node) for node in self.nodes])
        return csv

    def __str__(self):
        return 'Watson({}:{})'.format(*self.office)
