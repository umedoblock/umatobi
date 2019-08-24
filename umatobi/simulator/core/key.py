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

    def __init__(self, plain_key=b''):
        self.update(plain_key)

    def __str__(self):
        return '0x' + self.key.hex()

    def __int__(self):
        return int.from_bytes(self.key, 'big')

    def value(self):
        return self.key

    def update(self, plain_key=b''):
        if not isinstance(plain_key, bytes):
            raise ValueError('key must be bytes object.')
        if len(plain_key) == 0:
            plain_key = os.urandom(Key.KEY_OCTETS)
        elif len(plain_key) != Key.KEY_OCTETS:
            raise ValueError(f"key length is {len(plain_key)}, it must be {Key.KEY_OCTETS}.")
        self.key = plain_key
