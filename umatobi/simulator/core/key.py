import re, math, struct

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
    def plain_hex_to_plain_key(cls, plain_hex):
        plain_key = b''
        for hh in re.findall('..', plain_hex):
            octet = int(hh, 16)
            byte = int.to_bytes(octet, 1, 'big')
            plain_key += byte
        return plain_key

    #    oclock:   at 00:00 =>  at 03:00 =>       at 06:00
    #       key:     0x0000 =>    0x4000 =>         0x8000
    #  math_rad: 1 / 2 * pi =>       0.0 =>     3 / 2 * pi
    #  cos, sin:   0.0, 1.0 =>  1.0, 0.0 =>      0.0, -1.0
    # scale_rad:   0.0 * pi =>  0.5 * pi =>       1.0 * pi

    #    oclock:   at 06:00 =>  at 09:00 =>       at 11:59
    #       key:     0x8000 =>    0xc000 =>         0xffff
    #  math_rad: 3 / 2 * pi =>        pi => 1.001 / 2 * pi
    #  cos, sin:  0.0, -1.0 => -1.0, 0.0 =>  -0.001, 0.999
    # scale_rad:   1.0 * pi =>  1.5 * pi =>     1.999 * pi

    @classmethod
    def key_to_scale_rad(cls, key):
        rate = cls.key_to_int(key) / (1 << cls.KEY_BITS)
        scale_rad = (2 * math.pi) * rate
        return scale_rad

    @classmethod
    def scale_rad_to_math_rad(cls, scale_rad):
        math_rad = -scale_rad + math.pi / 2.0
        if math_rad < 0:
            math_rad += 2 * math.pi
        if math_rad > 2 * math.pi:
            math_rad -= 2 * math.pi
        return math_rad

    @classmethod
    def key_to_rxy(cls, key):
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

        scale_rad = cls.key_to_scale_rad(key)
        math_rad = cls.scale_rad_to_math_rad(scale_rad)
        cs = math.cos(math_rad)
        sn = math.sin(math_rad)

        m = 1.00
        x = cs * m
        y = sn * m

        return scale_rad, x, y

    @classmethod
    def key_to_int(cls, key):
        return int.from_bytes(key, 'big')

    @classmethod
    def memcmp(cls, a, b, size):
        unpacked_a = struct.unpack(f"{Key.KEY_OCTETS}B", a)
        unpacked_b = struct.unpack(f"{Key.KEY_OCTETS}B", b)

        for i in range(size):
            if unpacked_a[i] > unpacked_b[i]:
                return 1
            elif unpacked_a[i] < unpacked_b[i]:
                return -1
        return 0

    # copy keycmp() from
    # omoide/umatobi/trunk/sim/rgb/rgblib.c
    @classmethod
    def keycmp(cls, a, b):
        # 'Q' # unsigned long long 8 octets
    #   unpack_a = struct.unpack('4Q', a)
    #   unpack_b = struct.unpack('4Q', b)

    #   for i in range(Key.KEY_OCTETS // 8):
    #       if unpack_a[i] > unpack_b[i]:
    #           return 1
    #       elif unpack_a[i] < unpack_b[i]:
    #           return -1

        res1 = Key.memcmp(a, b, Key.KEY_OCTETS)
        if res1 == 0:
            return 0

        # memcpy(b_, b, DHT_KEYSIZE); b_[0] ^= 0x80
        b_ = int.to_bytes((b[0] ^ 0x80), 1, 'big')  + b[1:]
        res2 = Key.memcmp(b_, a, Key.KEY_OCTETS)
        res = -1
        if b[0] <= 0x7f:
            if res1 > 0 and res2 > 0:
                res = 1
        else:
            if res1 > 0 or res2 > 0:
                res = 1

        return res

    def __eq__(self, other):
        """object.__eq__() の help を読んで。"""
        result = Key.keycmp(self.key, other.key)
        if result == 0:
            return True
        else:
            return False

    def __ne__(self, other):
        """object.__ne__() の help を読んで。"""
        return not self == other

    def __gt__(self, other):
        """object.__gt__() の help を読んで。"""
        result = Key.keycmp(self.key, other.key)
        if result > 0:
            return True
        else:
            return False

    def __ge__(self, other):
        """object.__ge__() の help を読んで。"""
        return self > other or self == other

    def __lt__(self, other):
        """object.__lt__() の help を読んで。"""
        result = Key.keycmp(self.key, other.key)
        if result < 0:
            return True
        else:
            return False

    def __le__(self, other):
        """object.__le__() の help を読んで。"""
        return self < other or self == other

    def __init__(self, plain_key=b''):
        self.update(plain_key)

    def __str__(self):
        return '0x' + self.key.hex()

    def __int__(self):
        return Key.key_to_int(self.key)

    def value(self):
        return self.key

    def get_rxy(self):
        rxy = Key.key_to_rxy(self.key)
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
