from umatobi.constants import *

class Key(object):

    KEY_BITS = 256
    KEY_OCTETS = KEY_BITS // 8
# KEY_BYTES = KEY_OCTETS
#   >>> n = 1
#   >>> n.to_bytes(16, 'big')
#   b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01'
#   >>> b1 = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01'
#   >>> int.from_bytes(b1, 'big')
#   1

    def __init__(self, k=b''):
        self.update(k)

    def __str__(self):
        return self.key.kex()

    def __int__(self):
        return int.from_bytes(self.key, 'big')

    def value(self):
        return self.key

    def update(self, k=b''):
        if not isinstance(k, bytes):
            raise ValueError('key must be bytes object.')
        if len(k) == 0:
            k = os.urandom(Key.KEY_OCTETS)
        elif len(k) != Key.KEY_OCTETS:
            raise ValueError(f"key length is {len(k)}, it must be {Key.KEY_OCTETS}.")
        self.key = k
