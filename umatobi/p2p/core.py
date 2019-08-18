import threading
import socket
import os
import sys

from umatobi.constants import *
from umatobi.lib import formula
from umatobi.log import *

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
        self.udp_ip = (host, port)
        self.make_udpip()

        self._status = {}
        self.update_key()

    def release(self):
        if self.udp_sock:
            self.udp_sock.close()
          # self.udp_sock = None
          # ここで、close() する、udp_sock は、
          # bind() に成功し、有効に利用されていたudp_sockなのだから、
          # udp_sock に None を代入しない。

    def make_udpip(self, host=None, port=None):
        if not hasattr(self, 'udp_ip'):
           self.udp_ip = (None, None)

        if host is not None:
            self.udp_ip = (host, self.udp_ip[1])
        if port is not None:
            self.udp_ip = (self.udp_ip[0], port)

        if not all(self.udp_ip):
            return

        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            self.udp_sock.bind(self.udp_ip)
        except socket.error as raiz:
            self.udp_sock.close()
            self.udp_sock = None
            logger.error('cannot bind({}). reason={}'.format(self.udp_ip, raiz.args))

          # print('raiz.args =', raiz.args)
            if raiz.args == (98, 'Address already in use'):
                logger.error('指定した host(={}), port(={}) は使用済みでした。'.
                        format(*self.udp_ip))
            elif raiz.args == (13, 'Permission denied'):
                pass
        except OverflowError as raiz:
          # getsockaddrarg: port must be 0-65535.
            print('raiz.args =', raiz.args)
            self.udp_sock.close()
            self.udp_sock = None
            logger.error('cannot bind({}). reason={}'.format(self.udp_ip, raiz.args))

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

    def update_key(self, k=b''):
        if not isinstance(k, bytes):
            raise ValueError('key must be bytes object.')
        if len(k) == 0:
            k = os.urandom(KEY_OCTETS)
        elif len(k) != KEY_OCTETS:
            raise ValueError(f"key length is {len(k)}, it must be {KEY_OCTETS}.")
        self.key = k

    def get_status(self, type_='dict'):
        'node の各種情報を表示。'
        self._status['host'] = self.udp_ip[0]
        self._status['port'] = self.udp_ip[1]
        self._status['key'] = self.key
        return self._status

    def _key_hex(self):
        return formula._key_hex(self.key)
