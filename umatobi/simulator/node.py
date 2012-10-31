import sys, os
import struct
import math

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import p2p.core
from lib import formula

class Node(p2p.core.Node):

    _output = print

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
        self._output('keyID={:08x}'.format(self._keyID), file=file)
        self._output('  key={:s}'.format(self._key_hex()), file=file)
        self._output(' _rad= {:.3f} * PAI'.format(self._rad / math.pi),
                                                  file=file)
        self._output('   _x={: .3f}'.format(self._x), file=file)
        self._output('   _y={: .3f}'.format(self._y), file=file)

    def _key_hex(self):
        return formula._key_hex(self.key)

if __name__ == '__main__':
    node = Node('localhost', 10001)
    node.info()
