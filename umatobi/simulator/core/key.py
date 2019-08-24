import re, math

from umatobi.constants import *

class Key(object):

    KEY_BITS = 256
    KEY_HEXES = KEY_BITS // 4
    KEY_OCTETS = KEY_BITS // 8
# KEY_BYTES = KEY_OCTETS
#   >>> n = 1
#   >>> n.to_bytes(16, 'big')
#   b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01'
#   >>> b1 = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01'
#   >>> int.from_bytes(b1, 'big')
#   1

    @classmethod
    def plain_hex2plain_key(cls, plain_hex):
        plain_key = b''
        for hh in re.findall('..', plain_hex):
            octet = int(hh, 16)
            byte = int.to_bytes(octet, 1, 'big')
            plain_key += byte
        return plain_key

    @classmethod
    def key_to_norm_rad(cls, self):
        rate = int(self) / (1 << cls.KEY_BITS)
        norm_rad = (2 * math.pi) * rate
        return norm_rad

    @classmethod
    def norm_rad_to_math_rad(cls, norm_rad):
        math_rad = -norm_rad + math.pi / 2.0
        if math_rad < 0:
            math_rad += 2 * math.pi
        if math_rad > 2 * math.pi:
            math_rad -= 2 * math.pi
        return math_rad

    @classmethod
    def key2rxy(cls, self):
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

        norm_rad = cls.key_to_norm_rad(self)
        math_rad = cls.norm_rad_to_math_rad(norm_rad)
        cs = math.cos(math_rad)
        sn = math.sin(math_rad)

        m = 1.00
        x = cs * m
        y = sn * m

        return norm_rad, x, y

    def __init__(self, plain_key=b''):
        self.update(plain_key)

    def __str__(self):
        return '0x' + self.key.hex()

    def __int__(self):
        return int.from_bytes(self.key, 'big')

    def value(self):
        return self.key

    def get_rxy(self):
        rxy = Key.key2rxy(self)
        return rxy

    def update(self, plain_key=b''):
        if not isinstance(plain_key, bytes):
            raise ValueError(f'plain_key must be bytes object but it is {type(plain_key)} object')
        if len(plain_key) == 0:
            plain_key = os.urandom(Key.KEY_OCTETS)
        elif len(plain_key) != Key.KEY_OCTETS:
            raise ValueError(f"plain_key length is {len(plain_key)}, it must be {Key.KEY_OCTETS}.")

        # plain_key passes several checks !
        # plain_key is taken by Key class as key.
        self.key = plain_key
