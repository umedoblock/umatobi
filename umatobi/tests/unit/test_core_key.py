import os, unittest

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

    def test_core_key_update(self):
        k = Key()
        CoreKeyTests.assert_key_initance(self, k)

        key0 = k.key
        k.update()
        CoreKeyTests.assert_key_initance(self, k)
        self.assertNotEqual(k.key, key0)

        key_rand = os.urandom(32)
        k.update(key_rand)
        CoreKeyTests.assert_key_initance(self, k)
        self.assertEqual(k.key, key_rand)

    def test_core_key_fail_by_uncorrect_length(self):
        with self.assertRaises(ValueError) as cm:
            Key(b'+' * (Key.KEY_OCTETS + 1))
        the_exception = cm.exception
        self.assertEqual(the_exception.args[0], "key length is 33, it must be 32.")

        with self.assertRaises(ValueError) as cm:
            Key(b'-' * (Key.KEY_OCTETS - 1))
        the_exception = cm.exception
        self.assertEqual(the_exception.args[0], "key length is 31, it must be 32.")

    def test_core_key_fail_by_not_bytes(self):
        with self.assertRaises(ValueError) as cm:
            Key('0' * Key.KEY_OCTETS)
        the_exception = cm.exception
        self.assertEqual(the_exception.args[0], 'key must be bytes object.')

        with self.assertRaises(ValueError) as cm:
            Key(32 * Key.KEY_OCTETS)
        the_exception = cm.exception
        self.assertEqual(the_exception.args[0], 'key must be bytes object.')

if __name__ == '__main__':
    unittest.main()
