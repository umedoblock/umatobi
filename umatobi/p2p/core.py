import threading
import socket
import os
import sys

from umatobi.lib import formula

class Node(threading.Thread):
    '''Node class'''

    PACKET_SIZE = 2048

    _output = print

    def __init__(self, host, port):
        '''\
        node を初期化する。
        '''
        self._status = {}
        threading.Thread.__init__(self)
        tup = (host, port)
        self.host, self.port = tup

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.sock.bind(tup)
        except socket.error as raiz:
          # print('raiz.args =', raiz.args)
            if raiz.args == (98, 'Address already in use'):
                self._output('指定した host(={}), port(={}) は使用済みでした。'.
                        format(*tup))
            raise raiz

        self.update_key()

    def run(self):
        self._last_moment = threading.Event()
        self._last_moment.wait()

    def appear(self):
        self.start()

    def disappear(self):
        '''別れ, envoi'''
        if hasattr(self, '_last_moment'):
            self._last_moment.set()
        self.sock.close()
        self.join()

    def update_key(self, k=b''):
        if not k:
            k = os.urandom(16)
        self.key = k

    def get_status(self, type_='dict'):
        'node の各種情報を表示。'
        self._status['host'] = self.host
        self._status['port'] = self.port
        self._status['key'] = self.key
        return self._status

    def _key_hex(self):
        return formula._key_hex(self.key)
