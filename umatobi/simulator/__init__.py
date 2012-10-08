import threading
import sys, os
import socket
import sqlite3

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import p2p.core
from lib import jbytes_becomes_dict

__all__ = ['Node']

class Node(p2p.core.Node):
    def __init__(self, host, port):
        '''\
        simulator 用 node を初期化する。
        '''
        super().__init__(host, port)

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
        super().update_key(k=k)

        self._keyID = struct.unpack('>I', self.key[:4])[0]
        r, x, y = formula._key2rxy(self._keyID)
        self._rad, self._x, self._y = r, x, y

    def info(self, file=sys.stdout):
        'node の各種情報を表示。'
        super().info(file=file)
        print('keyID={:08x}'.format(self._keyID), file=file)
        print('  key={:s}'.format(self._key_hex()), file=file)
        print(' _rad= {:.3f} * PAI'.format(self._rad / math.pi), file=file)
        print('   _x={: .3f}'.format(self._x), file=file)
        print('   _y={: .3f}'.format(self._y), file=file)

    def _key_hex(self):
        return formula._key_hex(self.key)

class Relay(threading.Thread):
    SCHEMA = os.path.join(os.path.dirname(__file__), 'simulation_tables.schema')

    def __init__(self, watson, num_nodes, simulation_dir):
        threading.Thread.__init__(self)
        self.watson = watson
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.timeout_sec = 1
        socket.setdefaulttimeout(self.timeout_sec)
        self.simulation_dir = simulation_dir

        self._init_attrs()

        # thread start!
        self.start()

    def run(self):
        print('Relay(no={}) started!'.format(self.no))

    def _init_attrs(self):
        d = self._hello_watson()
        if not d:
            raise RuntimeError('relay._hello_watson() return None object. watson is {}'.format(self.watson))

        self.no = d['no']
        start_up = d['start_up']
        db_dir = os.path.join(self.simulation_dir, start_up)
        print('relay.simulation_dir =', self.simulation_dir)
        print('db_dir =', db_dir)
        self.relay_db = os.path.join(db_dir, 'relay.{}.db'.format(self.no))
        print('relay.relay_db =', self.relay_db)
        self.conn = sqlite3.connect(self.relay_db)

    def _hello_watson(self):
        tries = 0
        d = {}
        while tries < 3:
            try:
                self.sock.sendto(b'I am Relay.', self.watson)
                recved_msg, who = self.sock.recvfrom(1024)
            except socket.timeout as raiz:
                tries += 1
                continue
          # if self.watson == who:
            d = jbytes_becomes_dict(recved_msg)
            break
        print('self.watson =')
        print(self.watson)
        print('who =')
        print(who)
        print('d =')
        print(d)
        return d
