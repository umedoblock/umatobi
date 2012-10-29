import sys, os
import threading
import sqlite3
import socket
import multiprocessing

from . import darkness
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lib import make_logger, jbytes_becomes_dict

def make_darkness(simulation_dir, no, num_nodes, made_nodes, leave_there):
    darkness_ = darkness.Darkness(simulation_dir, no,
                                  num_nodes, made_nodes, leave_there)
    darkness_.start()
    darkness_.stop()

class Client(threading.Thread):
    SCHEMA = os.path.join(os.path.dirname(__file__), 'simulation_tables.schema')

    def __init__(self, watson, num_nodes, simulation_dir):
        threading.Thread.__init__(self)
        self.watson = watson
        self.simulation_dir = simulation_dir
        self.num_darkness = 1
        self.num_nodes = 4
        self.total_nodes = 0

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

    def run(self):
        self.logger.info('Client(no={}) started!'.format(self.no))

        self.darkness_processes = []
        for no in range(self.num_darkness):
            made_nodes = multiprocessing.Value('i', 0)
            darkness_process = \
                multiprocessing.Process(
                    target=make_darkness,
                    args=(self.db_dir, no, self.num_nodes, made_nodes, self.leave_there))
            darkness_process.start()
            self.darkness_processes.append(darkness_process)

        while True:
            try:
                recved, recved_addr = self.sock.recvfrom(1024)
            except socket.timeout:
                recved = b''
                continue

            if recved == b'break down.':
                self.logger.info('Client(no={}) got break down from {}.'.format(self.no, recved_addr))
                break

        self._release()

    def join(self):
        threading.Thread.join(self)
        self.logger.info('Client(no={}) thread joined.'.format(self.no))

    def _release(self):
        # TODO: #100 client.db をwatsonに送りつける。
        self.logger.info('Client(no={}) thread released.'.format(self.no))
        for no, darkness_process in enumerate(self.darkness_processes):
            darkness_process.join()

    def _init_attrs(self):
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
