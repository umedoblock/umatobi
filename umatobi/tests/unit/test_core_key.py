import os, re, unittest
from math import pi

from umatobi.simulator.core.key import Key

class CoreKeyTests(unittest.TestCase):

    @classmethod
    def assert_key_initance(cls, self, k):
        self.assertIsInstance(k, Key)
        self.assertIsInstance(k.key, bytes)
        self.assertEqual(len(k.key), Key.KEY_OCTETS)

    def test_core_key_plain_hex_to_plain_key(self):
        plain_hex = '31' * Key.KEY_OCTETS
        expected = b'\x31' * Key.KEY_OCTETS

        plain_key = Key.plain_hex_to_plain_key(plain_hex)
        self.assertEqual(plain_key, expected)

    def test_core_key_key_to_scale_rad(self):
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

    def test_core_key_scale_rad_to_math_rad(self):
        scale_rads = (  0.0 * pi, 0.5 * pi,       1.0 * pi,
                        1.0 * pi, 1.5 * pi,     1.999 * pi, 2.0 * pi)
        math_rads  = (1 / 2 * pi,      0.0,     3 / 2 * pi,
                      3 / 2 * pi,       pi, 1.001 / 2 * pi, 0.5 * pi)
        expected_rads = math_rads

        for scale_rad, expected_rad in zip(scale_rads, expected_rads):
            rad = Key.scale_rad_to_math_rad(scale_rad)
            self.assertAlmostEqual(rad, expected_rad, 2)

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

    def test_core_key_key_to_rxy(self):
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

    def test_core_key_key_to_int(self):
        expected_int = 0
        for i in range(Key.KEY_OCTETS):
            expected_int <<= 8
            expected_int += 0x31
        plain_key = b'\x31' * Key.KEY_OCTETS

        self.assertEqual(Key.key_to_int(plain_key), expected_int)

    def test_core_key_init_by_regular(self):
        k = Key(b'o' * Key.KEY_OCTETS)
        CoreKeyTests.assert_key_initance(self, k)
        self.assertEqual(k.key, b'o' * Key.KEY_OCTETS)

    def test_core_key_init_by_empty(self):
        k = Key()
        CoreKeyTests.assert_key_initance(self, k)

    def test_core_key_get_rxy(self):
        # key increases from 0x000...000 to 0xfff...fff.
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
            tup = tuple(zip(ko.get_rxy(), expected_rxy))
            for rxy, expected_value in zip(ko.get_rxy(), expected_rxy):
                self.assertAlmostEqual(rxy, expected_value, 3)

    def test_core_key_convert(self):
        octets = b''
        for i in range(Key.KEY_OCTETS):
            octets += int.to_bytes(i * 8, 1, 'big')
        ko = Key(octets)
        CoreKeyTests.assert_key_initance(self, ko)

        self.assertEqual(int(ko),  0x0008101820283038404850586068707880889098a0a8b0b8c0c8d0d8e0e8f0f8)
        self.assertEqual(str(ko), '0x0008101820283038404850586068707880889098a0a8b0b8c0c8d0d8e0e8f0f8')

    def test_core_key_update(self):
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

    def test_core_key_fail_by_incorrect_length(self):
        with self.assertRaises(ValueError) as cm:
            Key(b'+' * (Key.KEY_OCTETS + 1))
        the_exception = cm.exception
        self.assertEqual(the_exception.args[0], "plain_key length is 33, it must be 32.")

        with self.assertRaises(ValueError) as cm:
            Key(b'-' * (Key.KEY_OCTETS - 1))
        the_exception = cm.exception
        self.assertEqual(the_exception.args[0], "plain_key length is 31, it must be 32.")

    def test_core_key_fail_by_not_bytes(self):
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
