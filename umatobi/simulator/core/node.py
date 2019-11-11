import threading, socket, os, sys

from umatobi.simulator.core.key import Key
from umatobi.log import *
from umatobi.lib import *

class Node(threading.Thread):
    '''Node class'''

    PACKET_SIZE = 2048

    # Node()        <=> node.release()
    # node.appear() <=> node.disappear()

    def __init__(self, host=None, port=None):
        '''\
        node を初期化する。
        '''
        threading.Thread.__init__(self)
        self._last_moment = threading.Event()

        self.udp_sock = None
        self.udp_addr = (host, port)

        self._status = {}
        self.key = Key()

    def bind_udp(self, host, port):
        self.udp_sock, self.udp_addr, result = \
            sock_bind(self.udp_sock, host, port, 'v4', 'udp')
        return result

    def release(self):
        if self.udp_sock:
            self.udp_sock.close()
          # self.udp_sock = None
          # ここで、close() する、udp_sock は、
          # bind() に成功し、有効に利用されていたudp_sockなのだから、
          # udp_sock に None を代入しない。

    def run(self):
        self._last_moment.wait()

    def appear(self):
        self.start()

    def disappear(self):
        '''別れ, envoi'''
        self.release()
        if hasattr(self, '_last_moment'):
            self._last_moment.set()
        self.join()

    def get_status(self, type_='dict'):
        'node の各種情報を表示。'
        self._status['host'] = self.udp_addr[0]
        self._status['port'] = self.udp_addr[1]
        self._status['key'] = self.key.value()
        return self._status
