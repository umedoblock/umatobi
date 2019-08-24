import os, re, unittest

from umatobi.simulator.core.key import Key

class CoreKeyTests(unittest.TestCase):

    @classmethod
    def assert_key_initance(cls, self, k):
        self.assertIsInstance(k, Key)
        self.assertIsInstance(k.key, bytes)
        self.assertEqual(len(k.key), Key.KEY_OCTETS)

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

        expected = {
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

        for name, expected_int_rxy in expected.items():
            expected_int, expected_rxy = expected_int_rxy

            an_hex = name.replace('key0x', '')
            plain_hex = an_hex + '0' * (Key.KEY_HEXES - 1)
            octets = [int.to_bytes(int(hh, 16), 1, 'big') for hh in re.findall('..', plain_hex)]
            plain_key = b''.join(octets)

          # print('plain_key =', plain_key)
          # print('len(plain_key) =', len(plain_key))
            ko = Key(plain_key)
            # ko means key octets not key object.
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
