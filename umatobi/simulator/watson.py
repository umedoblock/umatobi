import threading
import os
import sys
import socket
import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lib import make_logger, dict_becomes_jbytes

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

        self.logger = make_logger(self.db_dir, 'watson')
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
          # self.logger.info('passed time {:.3f}'.format(self.passed_time()))

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
        self.logger.info('watson._release_clients()')
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
