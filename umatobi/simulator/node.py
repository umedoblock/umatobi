import sys, os
import struct
import math
import pickle

import p2p.core
from lib import formula
from lib import current_isoformat_time

class Node(p2p.core.Node):

    _output = print

    def __init__(self, host, port, id, good_bye_with_darkness, _queue_darkness):
        '''\
        simulator 用 node を初期化する。
        '''
        super().__init__(host, port)
        self.id = id
        self.good_bye_with_darkness = good_bye_with_darkness
        self._queue_darkness = _queue_darkness
        self._rad, self._x, self._y = 0.0, 0.0, 0.0

    def run(self):
      # print('{} started.'.format(self))
        d = {}
        d['id'] = self.id
        d['host'] = self.host
        d['port'] = self.port
        while not self.good_bye_with_darkness.wait(timeout=1):
            self.update_key()
            key_hex = self._key_hex()
          # print('{} key_hex = {}'.format(self, key_hex))

            d['key'] = key_hex
            d['status'] = 'active'
            self.to_darkness(d)

        d['key'] = None
        d['status'] = 'inactive'
        self.to_darkness(d)
      # print('{} good bye(host={}, port={})'.format(self, self.host, self.port))

    def to_darkness(self, obj):
        moment = current_isoformat_time()
        pds = pickle.dumps(obj)
        self._queue_darkness.put((moment, pds))

    def appear(self):
        super().appear()

    def disappear(self):
        super().disappear()

    def __str__(self):
        return 'Node(id={})'.format(self.id)

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

    def get_status(self, type_='dict'):
        'node の各種情報を表示。'
        super().get_status(type_)
        self._status['_keyID'] = self._keyID

      # self._status['_rad.float'] = '{:.3f} * PAI'.format(self._rad / math.pi)
        key_rate = (self._keyID / (1 << 32))
        hour, mod = divmod(key_rate, 1 / 12)
        self._status['_rad.hour'] = '({} / 12 + {:.3f}) * 2 * PAI'.format(int(hour), mod)
        self._status['_x'] = self._x
        self._status['_y'] = self._y

        return self._status
