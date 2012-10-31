import threading
import socket
import os
import sys

class Node(threading.Thread):
    '''Node class'''

    PACKET_SIZE = 2048

    _output = print

    def __init__(self, host, port):
        '''\
        node を初期化する。
        '''
        threading.Thread.__init__(self)
        tup = (host, port)
        self.host, self.port = tup

        self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.recv_sock.bind(tup)
        except socket.error as raiz:
          # print('raiz.args =', raiz.args)
            if raiz.args == (98, 'Address already in use'):
                self._output('指定した host(={}), port(={}) は使用済みでした。'.
                        format(*tup))
            raise raiz

        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.update_key()

    def update_key(self, k=b''):
        if not k:
            k = os.urandom(16)
        self.key = k

    def info(self, file=sys.stdout):
        'node の各種情報を表示。'
        self._output(' host={}'.format(self.host), file=file)
        self._output(' port={}'.format(self.port), file=file)

if __name__ == '__main__':
    node = Node('localhost', 10000)
    node.info()
