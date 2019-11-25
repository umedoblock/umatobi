# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import os, re, unittest
from math import pi

from umatobi.simulator.core.key import Key

class CoreKeyTests(unittest.TestCase):

    @classmethod
    def assert_key_initance(cls, self, k):
        self.assertIsInstance(k, Key)
        self.assertIsInstance(k.key, bytes)
        self.assertEqual(len(k.key), Key.KEY_OCTETS)

    def test_plain_hex_to_plain_key(self):
        plain_hex = '31' * Key.KEY_OCTETS
        expected = b'\x31' * Key.KEY_OCTETS

        plain_key = Key.plain_hex_to_plain_key(plain_hex)
        self.assertEqual(plain_key, expected)

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

    def test_key_to_scale_rad(self):
        plain_hex = b'\x00' + b'\x00' * (Key.KEY_OCTETS - 1)
        scale_rad = Key.key_to_scale_rad(plain_hex)
        self.assertEqual(scale_rad, 0.0 * 2.0 * pi)

        plain_hex = b'\x40' + b'\x00' * (Key.KEY_OCTETS - 1)
        scale_rad = Key.key_to_scale_rad(plain_hex)
        self.assertEqual(scale_rad, 0.25 * 2.0 * pi)

        plain_hex = b'\x80' + b'\x00' * (Key.KEY_OCTETS - 1)
        scale_rad = Key.key_to_scale_rad(plain_hex)
        self.assertEqual(scale_rad, 0.50 * 2.0 * pi)

        plain_hex = b'\xc0' + b'\x00' * (Key.KEY_OCTETS - 1)
        scale_rad = Key.key_to_scale_rad(plain_hex)
        self.assertEqual(scale_rad, 0.75 * 2.0 * pi)

        plain_hex = b'\xff' * Key.KEY_OCTETS
        scale_rad = Key.key_to_scale_rad(plain_hex)
        self.assertAlmostEqual(scale_rad, 1.999 * pi, 2)

    def test_scale_rad_to_math_rad(self):
        scale_rads = (  0.0 * pi, 0.5 * pi,       1.0 * pi,
                        1.0 * pi, 1.5 * pi,     1.999 * pi, 2.0 * pi)
        math_rads  = (1 / 2 * pi,      0.0,     3 / 2 * pi,
                      3 / 2 * pi,       pi, 1.001 / 2 * pi, 0.5 * pi)
        expected_rads = math_rads

        for scale_rad, expected_rad in zip(scale_rads, expected_rads):
            rad = Key.scale_rad_to_math_rad(scale_rad)
            self.assertAlmostEqual(rad, expected_rad, 2)

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

    AROUND_THE_CLOCK = {
        #  name,  int                       , (rxy)=(radius, cos, sin)
        'key0x0': (0x0 << (Key.KEY_BITS - 4), (0.000, 0.000, 1.000)),
        'key0x1': (0x1 << (Key.KEY_BITS - 4), (0.393, 0.383, 0.924)),
        'key0x2': (0x2 << (Key.KEY_BITS - 4), (0.785, 0.707, 0.707)),
        'key0x3': (0x3 << (Key.KEY_BITS - 4), (1.178, 0.924, 0.383)),
        'key0x4': (0x4 << (Key.KEY_BITS - 4), (1.571, 1.000, 0.000)),
        'key0x5': (0x5 << (Key.KEY_BITS - 4), (1.963, 0.924,-0.383)),
        'key0x6': (0x6 << (Key.KEY_BITS - 4), (2.356, 0.707,-0.707)),
        'key0x7': (0x7 << (Key.KEY_BITS - 4), (2.749, 0.383,-0.924)),
        'key0x8': (0x8 << (Key.KEY_BITS - 4), (3.142,-0.000,-1.000)),
        'key0x9': (0x9 << (Key.KEY_BITS - 4), (3.534,-0.383,-0.924)),
        'key0xa': (0xa << (Key.KEY_BITS - 4), (3.927,-0.707,-0.707)),
        'key0xb': (0xb << (Key.KEY_BITS - 4), (4.320,-0.924,-0.383)),
        'key0xc': (0xc << (Key.KEY_BITS - 4), (4.712,-1.000, 0.000)),
        'key0xd': (0xd << (Key.KEY_BITS - 4), (5.105,-0.924, 0.383)),
        'key0xe': (0xe << (Key.KEY_BITS - 4), (5.498,-0.707, 0.707)),
        'key0xf': (0xf << (Key.KEY_BITS - 4), (5.890,-0.383, 0.924)),
    }

    def test_key_to_rxy(self):
        for name, expected_int_rxy in CoreKeyTests.AROUND_THE_CLOCK.items():
            expected_int, expected_rxy = expected_int_rxy

            an_hex = name.replace('key0x', '')
            plain_hex = an_hex + '0' * (Key.KEY_HEXES - 1)
            plain_key = b''
            for hh in re.findall('..', plain_hex):
                octet = int(hh, 16)
                byte = int.to_bytes(octet, 1, 'big')
                plain_key += byte

            rxy = Key.key_to_rxy(plain_key)

            self.assertIsInstance(rxy, tuple)
            for rxy, expected_value in zip(rxy, expected_rxy):
                self.assertAlmostEqual(rxy, expected_value, 3)

    def test_key_to_int(self):
        expected_int = 0
        for i in range(Key.KEY_OCTETS):
            expected_int <<= 8
            expected_int += 0x31
        plain_key = b'\x31' * Key.KEY_OCTETS

        self.assertEqual(Key.key_to_int(plain_key), expected_int)

    def test_memcmp(self):
        pass

    def test_key_keycmp_simple(self):
        # b'\xff' * 16
        # int.to_bytes(255, 1, 'big')
        # int.to_bytes(0, 1, 'big')
        keyffff = b'\xff' * Key.KEY_OCTETS
        keyfffe = b'\xff' * (Key.KEY_OCTETS-1) + b'\xfe'
        key7fff = b'\x7f' + b'\xff' * (Key.KEY_OCTETS-1)
        key7ffe = b'\x7f' + b'\xff' * (Key.KEY_OCTETS-2) + b'\xfe'

        key0000 = b'\x00' * Key.KEY_OCTETS
        key0001 = b'\x00' * (Key.KEY_OCTETS-1) + b'\x01'
        key8000 = b'\x80' + b'\x00' * (Key.KEY_OCTETS-1)
        key8001 = b'\x80' + b'\x00' * (Key.KEY_OCTETS-2) + b'\x01'

        self.assertEqual(Key.KEY_OCTETS, 32)
        self.assertEqual(len(keyffff), Key.KEY_OCTETS)
        self.assertEqual(len(keyfffe), Key.KEY_OCTETS)
        self.assertEqual(len(key7fff), Key.KEY_OCTETS)
        self.assertEqual(len(key7ffe), Key.KEY_OCTETS)
        self.assertEqual(len(key0000), Key.KEY_OCTETS)
        self.assertEqual(len(key0001), Key.KEY_OCTETS)
        self.assertEqual(len(key8000), Key.KEY_OCTETS)
        self.assertEqual(len(key8001), Key.KEY_OCTETS)

        # Greater means Red, Less means Green, Eq means White

        self.assertEqual(Key.keycmp(key0000, key0000), 0)   # eq     White
        self.assertGreater(Key.keycmp(key0001, key0000), 0) # + 1    Red
        self.assertGreater(Key.keycmp(key7fff, key0000), 0) # + 7fff Red
        self.assertLess(Key.keycmp(key8000, key0000), 0)    # + 8000 Green
        self.assertLess(Key.keycmp(keyffff, key0000), 0)    # - 1    Green

        self.assertEqual(Key.keycmp(key7fff, key7fff), 0)   # eq
        self.assertGreater(Key.keycmp(key8000, key7fff), 0) # + 1
        self.assertGreater(Key.keycmp(keyfffe, key7fff), 0) # + 7fff
        self.assertLess(Key.keycmp(keyffff, key7fff), 0)    # + 8000
        self.assertLess(Key.keycmp(key7ffe, key7fff), 0)    # -1
        self.assertLess(Key.keycmp(key0000, key7fff), 0)    # zero

        self.assertEqual(Key.keycmp(key8000, key8000), 0)   # eq
        self.assertGreater(Key.keycmp(key8001, key8000), 0) # + 1
        self.assertGreater(Key.keycmp(keyffff, key8000), 0) # + 7fff
        self.assertLess(Key.keycmp(key0000, key8000), 0)    # + 8000
        self.assertLess(Key.keycmp(key7fff, key8000), 0)    # -1

        self.assertEqual(Key.keycmp(keyffff, keyffff), 0)   # eq
        self.assertGreater(Key.keycmp(key0000, keyffff), 0) # + 1
        self.assertGreater(Key.keycmp(key7ffe, keyffff), 0) # + 7fff
        self.assertLess(Key.keycmp(key7fff, keyffff), 0)    # + 8000
        self.assertLess(Key.keycmp(keyfffe, keyffff), 0)    # -1

    def test_keycmp_boundary(self):
        key0000 = b'\x00' * Key.KEY_OCTETS
        keyffff = b'\xff' * Key.KEY_OCTETS

        key1fff = b'\x1f' + b'\xff' * (Key.KEY_OCTETS-1)
        key2000 = b'\x20' + b'\x00' * (Key.KEY_OCTETS-1)
        key2001 = b'\x20' + b'\x00' * (Key.KEY_OCTETS-2) + b'\x01'

        key5fff = b'\x5f' + b'\xff' * (Key.KEY_OCTETS-1)
        key6000 = b'\x60' + b'\x00' * (Key.KEY_OCTETS-1)
        key6001 = b'\x60' + b'\x00' * (Key.KEY_OCTETS-2) + b'\x01'

        key9fff = b'\x9f' + b'\xff' * (Key.KEY_OCTETS-1)
        keya000 = b'\xa0' + b'\x00' * (Key.KEY_OCTETS-1)
        keya001 = b'\xa0' + b'\x00' * (Key.KEY_OCTETS-2) + b'\x01'

        keydfff = b'\xdf' + b'\xff' * (Key.KEY_OCTETS-1)
        keye000 = b'\xe0' + b'\x00' * (Key.KEY_OCTETS-1)
        keye001 = b'\xe0' + b'\x00' * (Key.KEY_OCTETS-2) + b'\x01'

        self.assertEqual(Key.KEY_OCTETS, 32)
        self.assertEqual(len(key0000), Key.KEY_OCTETS)
        self.assertEqual(len(keyffff), Key.KEY_OCTETS)
        self.assertEqual(len(key1fff), Key.KEY_OCTETS)
        self.assertEqual(len(key2000), Key.KEY_OCTETS)
        self.assertEqual(len(key2001), Key.KEY_OCTETS)
        self.assertEqual(len(key5fff), Key.KEY_OCTETS)
        self.assertEqual(len(key6000), Key.KEY_OCTETS)
        self.assertEqual(len(key6001), Key.KEY_OCTETS)
        self.assertEqual(len(key9fff), Key.KEY_OCTETS)
        self.assertEqual(len(keya000), Key.KEY_OCTETS)
        self.assertEqual(len(keya001), Key.KEY_OCTETS)
        self.assertEqual(len(keydfff), Key.KEY_OCTETS)
        self.assertEqual(len(keye000), Key.KEY_OCTETS)
        self.assertEqual(len(keye001), Key.KEY_OCTETS)

        # Greater means Red, Less means Green, Eq means White

        self.assertEqual(Key.keycmp(key2000, key2000), 0)   # eq     White
        self.assertGreater(Key.keycmp(key2001, key2000), 0) # + 1    Red
        self.assertGreater(Key.keycmp(key9fff, key2000), 0) # + 7fff Red
        self.assertLess(Key.keycmp(keya000, key2000), 0)    # + 8000 Green
        self.assertLess(Key.keycmp(key1fff, key2000), 0)    # - 1    Green
        self.assertLess(Key.keycmp(keyffff, key2000), 0)    # end    Green
        self.assertLess(Key.keycmp(key0000, key2000), 0)    # zero   Green

        self.assertEqual(Key.keycmp(key6000, key6000), 0)   # eq     White
        self.assertGreater(Key.keycmp(key6001, key6000), 0) # + 1    Red
        self.assertGreater(Key.keycmp(keydfff, key6000), 0) # + 7fff Red
        self.assertLess(Key.keycmp(keye000, key6000), 0)    # + 8000 Green
        self.assertLess(Key.keycmp(key5fff, key6000), 0)    # - 1    Green
        self.assertLess(Key.keycmp(keyffff, key6000), 0)    # end    Green
        self.assertLess(Key.keycmp(key0000, key6000), 0)    # zero   Green

        self.assertEqual(Key.keycmp(keya000, keya000), 0)   # eq     White
        self.assertGreater(Key.keycmp(keya001, keya000), 0) # + 1    Red
        self.assertGreater(Key.keycmp(key1fff, keya000), 0) # + 7fff Red
        self.assertLess(Key.keycmp(key2000, keya000), 0)    # + 8000 Green
        self.assertLess(Key.keycmp(key9fff, keya000), 0)    # - 1    Green
        self.assertGreater(Key.keycmp(keyffff, keya000), 0) # end    Red
        self.assertGreater(Key.keycmp(key0000, keya000), 0) # zero   Red

        self.assertEqual(Key.keycmp(keye000, keye000), 0)   # eq     White
        self.assertGreater(Key.keycmp(keye001, keye000), 0) # + 1    Red
        self.assertGreater(Key.keycmp(key5fff, keye000), 0) # + 7fff Red
        self.assertLess(Key.keycmp(key6000, keye000), 0)    # + 8000 Green
        self.assertLess(Key.keycmp(keydfff, keye000), 0)    # - 1    Green
        self.assertGreater(Key.keycmp(keyffff, keye000), 0) # end    Red
        self.assertGreater(Key.keycmp(key0000, keye000), 0) # zero   Red

  # def test___eq__(self):
  #     pass

  # def test___ne__(self):
  #     pass

  # def test___gt__(self):
  #     pass

  # def test___ge__(self):
  #     pass

  # def test___lt__(self):
  #     pass

  # def test___le__(self):
  #     pass

    def test_key_richcmp_simple(self):
        keyffff = Key(b'\xff' * Key.KEY_OCTETS)
        keyfffe = Key(b'\xff' * (Key.KEY_OCTETS-1) + b'\xfe')
        key7fff = Key(b'\x7f' + b'\xff' * (Key.KEY_OCTETS-1))
        key7ffe = Key(b'\x7f' + b'\xff' * (Key.KEY_OCTETS-2) + b'\xfe')

        key0000 = Key(b'\x00' * Key.KEY_OCTETS)
        key0001 = Key(b'\x00' * (Key.KEY_OCTETS-1) + b'\x01')
        key8000 = Key(b'\x80' + b'\x00' * (Key.KEY_OCTETS-1))
        key8001 = Key(b'\x80' + b'\x00' * (Key.KEY_OCTETS-2) + b'\x01')

        # Greater means Red, Less means Green, Eq means White

        self.assertEqual(key0000, key0000)   # eq     White
        self.assertGreater(key0001, key0000) # + 1    Red
        self.assertGreater(key7fff, key0000) # + 7fff Red
        self.assertLess(key8000, key0000)    # + 8000 Green
        self.assertLess(keyffff, key0000)    # - 1    Green

        self.assertEqual(key7fff, key7fff)   # eq
        self.assertGreater(key8000, key7fff) # + 1
        self.assertGreater(keyfffe, key7fff) # + 7fff
        self.assertLess(keyffff, key7fff)    # + 8000
        self.assertLess(key7ffe, key7fff)    # -1
        self.assertLess(key0000, key7fff)    # zero

        self.assertEqual(key8000, key8000)   # eq
        self.assertGreater(key8001, key8000) # + 1
        self.assertGreater(keyffff, key8000) # + 7fff
        self.assertLess(key0000, key8000)    # + 8000
        self.assertLess(key7fff, key8000)    # -1

        self.assertEqual(keyffff, keyffff)   # eq
        self.assertGreater(key0000, keyffff) # + 1
        self.assertGreater(key7ffe, keyffff) # + 7fff
        self.assertLess(key7fff, keyffff)    # + 8000
        self.assertLess(keyfffe, keyffff)    # -1

    def test_key_richcmp_boundary(self):
        key0000 = Key(b'\x00' * Key.KEY_OCTETS)
        keyffff = Key(b'\xff' * Key.KEY_OCTETS)

        key1fff = Key(b'\x1f' + b'\xff' * (Key.KEY_OCTETS-1))
        key2000 = Key(b'\x20' + b'\x00' * (Key.KEY_OCTETS-1))
        key2001 = Key(b'\x20' + b'\x00' * (Key.KEY_OCTETS-2) + b'\x01')

        key5fff = Key(b'\x5f' + b'\xff' * (Key.KEY_OCTETS-1))
        key6000 = Key(b'\x60' + b'\x00' * (Key.KEY_OCTETS-1))
        key6001 = Key(b'\x60' + b'\x00' * (Key.KEY_OCTETS-2) + b'\x01')

        key9fff = Key(b'\x9f' + b'\xff' * (Key.KEY_OCTETS-1))
        keya000 = Key(b'\xa0' + b'\x00' * (Key.KEY_OCTETS-1))
        keya001 = Key(b'\xa0' + b'\x00' * (Key.KEY_OCTETS-2) + b'\x01')

        keydfff = Key(b'\xdf' + b'\xff' * (Key.KEY_OCTETS-1))
        keye000 = Key(b'\xe0' + b'\x00' * (Key.KEY_OCTETS-1))
        keye001 = Key(b'\xe0' + b'\x00' * (Key.KEY_OCTETS-2) + b'\x01')

        # Greater means Red, Less means Green, Eq means White

        self.assertEqual(key2000, key2000)   # eq     White
        self.assertGreater(key2001, key2000) # + 1    Red
        self.assertGreater(key9fff, key2000) # + 7fff Red
        self.assertLess(keya000, key2000)    # + 8000 Green
        self.assertLess(key1fff, key2000)    # - 1    Green
        self.assertLess(keyffff, key2000)    # end    Green
        self.assertLess(key0000, key2000)    # zero   Green

        self.assertEqual(key6000, key6000)   # eq     White
        self.assertGreater(key6001, key6000) # + 1    Red
        self.assertGreater(keydfff, key6000) # + 7fff Red
        self.assertLess(keye000, key6000)    # + 8000 Green
        self.assertLess(key5fff, key6000)    # - 1    Green
        self.assertLess(keyffff, key6000)    # end    Green
        self.assertLess(key0000, key6000)    # zero   Green

        self.assertEqual(keya000, keya000)   # eq     White
        self.assertGreater(keya001, keya000) # + 1    Red
        self.assertGreater(key1fff, keya000) # + 7fff Red
        self.assertLess(key2000, keya000)    # + 8000 Green
        self.assertLess(key9fff, keya000)    # - 1    Green
        self.assertGreater(keyffff, keya000) # end    Red
        self.assertGreater(key0000, keya000) # zero   Red

        self.assertEqual(keye000, keye000)   # eq     White
        self.assertGreater(keye001, keye000) # + 1    Red
        self.assertGreater(key5fff, keye000) # + 7fff Red
        self.assertLess(key6000, keye000)    # + 8000 Green
        self.assertLess(keydfff, keye000)    # - 1    Green
        self.assertGreater(keyffff, keye000) # end    Red
        self.assertGreater(key0000, keye000) # zero   Red

    def test_key_init_by_regular(self):
        k = Key(b'o' * Key.KEY_OCTETS)
        CoreKeyTests.assert_key_initance(self, k)
        self.assertEqual(k.key, b'o' * Key.KEY_OCTETS)

    def test_key_init_by_empty(self):
        k = Key()
        CoreKeyTests.assert_key_initance(self, k)

    def test___str__(self):
        pass

    def test___int__(self):
        octets = b''
        for i in range(Key.KEY_OCTETS):
            octets += int.to_bytes(i * 8, 1, 'big')
        ko = Key(octets)
        CoreKeyTests.assert_key_initance(self, ko)

        self.assertEqual(int(ko),  0x0008101820283038404850586068707880889098a0a8b0b8c0c8d0d8e0e8f0f8)
        self.assertEqual(str(ko), '0x0008101820283038404850586068707880889098a0a8b0b8c0c8d0d8e0e8f0f8')

    def test_value(self):
        pass

    def test_get_rxy(self):
        # key increases from 0x000..000 to 0xfff..fff.
        #
        # oclock turns clock wise.
        # key is on oclock.
        #
        # Therefore key share direction of movement and origin with oclock.
        #
        # This means that key start at zero oclock to at twelve oclock
        # like turning a oclock.
        #
        # PAY ATTENTION TO BELOW.
        #
        # key and clock combine radius.
        # This means that radius move pi/2, 0, 3*pi/2, pi to pi/2.
        #
        # I'll show you above means with below asserts.

        for name, expected_int_rxy in CoreKeyTests.AROUND_THE_CLOCK.items():
            expected_int, expected_rxy = expected_int_rxy

            an_hex = name.replace('key0x', '')
            plain_hex = an_hex + '0' * (Key.KEY_HEXES - 1)
            plain_key = b''
            for hh in re.findall('..', plain_hex):
                octet = int(hh, 16)
                byte = int.to_bytes(octet, 1, 'big')
                plain_key += byte

          # print('plain_key =', plain_key)
          # print('len(plain_key) =', len(plain_key))
            ko = Key(plain_key)
            #  ko means key object.
            # kos means key octets.
            CoreKeyTests.assert_key_initance(self, ko)

            self.assertEqual(int(ko), expected_int)
            for rxy, expected_value in zip(ko.get_rxy(), expected_rxy):
                self.assertAlmostEqual(rxy, expected_value, 3)

    def test_update(self):
        k = Key()
        CoreKeyTests.assert_key_initance(self, k)

        key0 = k.key
        k.update()
        CoreKeyTests.assert_key_initance(self, k)
        self.assertNotEqual(k.key, key0)

        key_rand = os.urandom(Key.KEY_OCTETS)
        k.update(key_rand)
        CoreKeyTests.assert_key_initance(self, k)
        self.assertEqual(k.key, key_rand)

    # done, at least test

    # fail test

    def test_fail_by_incorrect_length(self):
        with self.assertRaises(ValueError) as cm:
            Key(b'+' * (Key.KEY_OCTETS + 1))
        the_exception = cm.exception
        self.assertEqual(the_exception.args[0], "plain_key length is 33, it must be 32.")

        with self.assertRaises(ValueError) as cm:
            Key(b'-' * (Key.KEY_OCTETS - 1))
        the_exception = cm.exception
        self.assertEqual(the_exception.args[0], "plain_key length is 31, it must be 32.")

    def test_fail_by_not_bytes(self):
        with self.assertRaises(ValueError) as cm:
            Key('0' * Key.KEY_OCTETS)
        the_exception = cm.exception
        self.assertEqual(the_exception.args[0], "plain_key must be bytes object but it is <class 'str'> object")

        with self.assertRaises(ValueError) as cm:
            Key(32 * Key.KEY_OCTETS)
        the_exception = cm.exception
        self.assertEqual(the_exception.args[0], "plain_key must be bytes object but it is <class 'int'> object")

if __name__ == '__main__':
    unittest.main()
