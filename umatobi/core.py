import threading
import socket
import os
import sys
import struct
import math

class Umatobi(object):
    def __init__(self, ip, port):
        self._red = []
        self._green = []
        self._blue = []

class RGB(object):
    pass

class Node(threading.Thread):
    '''Node class'''

    PACKET_SIZE = 2048

    def __init__(self, host, port):
        '''\
        node を初期化する。
        '''
        threading.Thread.__init__(self)
        self.host = host
        self.port = port

        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        tup = host, port
        self.recv_sock.bind(tup)

        self.update_key()

        self.info()
        print('node initilized.')

    def update_key(self, k=b''):
        '''\
        how to mapping ? key to circle.
        key は '0' * 16 から 'f' * 16 までの範囲の値です。
        key は 0 時をゼロとして時計回り順で増加していきます。
        つまり、時計の時間と Key の値の関係は以下の通りです。
         0 時: 0000000000000000
         3 時: 4000000000000000
         6 時: 8000000000000000
         9 時: c000000000000000
        12 時: ffffffffffffffff
        '''
        if not k:
            k = os.urandom(16)
        self._keyID = struct.unpack('>I', k[:4])[0]
        self.key = k
        self._key2rxy(self._keyID)

    def info(self, file=sys.stdout):
        'node の各種情報を表示。'
        print(' host={}'.format(self.host), file=file)
        print(' port={}'.format(self.port), file=file)
        print('keyID={:08x}'.format(self._keyID), file=file)
        print('  key={:s}'.format(self._key_hex()), file=file)
        print(' _rad= {:.3f} * PAI'.format(self._rad / math.pi), file=file)
        print('   _x={: .3f}'.format(self._x), file=file)
        print('   _y={: .3f}'.format(self._y), file=file)

    def _key_hex(self):
        'key を16進で表現する。'
        fmt = '>' + 'I' * (len(self.key) // 4)
        hexes = struct.unpack(fmt, self.key)
        hex_str = ['{:08x}'.format(hex_) for hex_ in hexes]
        return ''.join(hex_str)

    def _key2rxy(self, _keyID):
        '''\
        時計を単位円として考えてください。
        時計の9時から3時の方向にx軸を引き、
        時計の6時から12時の方向にy軸を引いてください。
        key の値は0時をゼロとし、時計回り順で、
        12時(最大値:fff...fff)まで増加することを思い出してください。

        radの意味を理解しにくいかもしれません。
        理解しなくて良いですが、簡単には、
        rad = 2 * PAI  * (今何時？ / 12.0)
        です。
        '''
        rad = (2.0 * math.pi) * (_keyID / 4294967296)

        cs =  math.cos(rad + (3.0 * math.pi / 2.0 ))
        sn = -math.sin(rad + (3.0 * math.pi / 2.0 ))

        m = 1.00
        self._x = cs * m
        self._y = sn * m
        self._rad = rad

if __name__ == '__main__':
    node = Node('localhost', 10000)
