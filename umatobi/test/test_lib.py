import os, sys, datetime, shutil
import unittest

from umatobi.test import *
from umatobi.log import logger, make_logger
from umatobi import lib
from umatobi.lib.formula import keycmp

class LibTests(unittest.TestCase):

    def test_SIMULATION_DIR(self):
        self.assertEqual('test/umatobi-simulation', SIMULATION_DIR)

    def test_master_hand(self):
        y15s_time = lib.current_y15sformat_time()
        self.assertEqual(lib.get_master_hand(y15s_time), f"{y15s_time}/{MASTER_HAND}")

    def test_master_hand_path(self):
        y15s_time = lib.current_y15sformat_time()
        self.assertEqual(lib.get_master_hand_path(SIMULATION_DIR, y15s_time), f"test/umatobi-simulation/{y15s_time}/{MASTER_HAND}")

    def test_make_log_dir(self):
        special_dir = SIMULATION_DIR + "-special"
        self.assertFalse(os.path.isdir(special_dir))
        tlogger = make_logger(log_dir=special_dir, name='special', id_=None, level="INFO")
        self.assertTrue(os.path.isdir(special_dir))
        shutil.rmtree(special_dir)

        self.assertFalse(os.path.isdir(special_dir))
        tlogger = make_logger(log_dir=special_dir, name='special', id_=10, level="INFO")
        self.assertTrue(os.path.isdir(special_dir))
        shutil.rmtree(special_dir)

        special_dir = SIMULATION_DIR + "-special2"
        self.assertFalse(os.path.isdir(special_dir))
        tlogger = make_logger(log_dir=special_dir, name='', id_=None, level="INFO")
        self.assertTrue(os.path.isdir(special_dir))
        shutil.rmtree(special_dir)

        self.assertFalse(os.path.isdir(special_dir))
        tlogger = make_logger(log_dir=special_dir, name='', id_=10, level="INFO")
        self.assertTrue(os.path.isdir(special_dir))
        shutil.rmtree(special_dir)

    def test_log_path(self):
        tlogger = make_logger(log_dir=SIMULATION_DIR, name='test_logger', id_=None, level="INFO")
        self.assertEqual('test/umatobi-simulation/test_logger.log', tlogger.log_path)

        tlogger = make_logger(log_dir=SIMULATION_DIR, name='test_logger', id_=888, level="INFO")
        self.assertEqual('test/umatobi-simulation/test_logger.888.log', tlogger.log_path)

    def test_make_start_up_orig(self):
        start_up_orig = lib.make_start_up_orig()
        self.assertIsInstance(start_up_orig, datetime.datetime)

    def test_curren_y15sformat_time(self):
        # Y15S_FORMAT='%Y-%m-%dT%H%M%S'
        y15s = lib.current_y15sformat_time()
        self.assertIsInstance(y15s, str)
        self.assertRegex(y15s, r"\A\d{4}-\d{2}-\d{2}T\d{6}\Z")

    def test_y15sformat_time(self):
        start_up_orig = lib.make_start_up_orig()
        # Y15S_FORMAT='%Y-%m-%dT%H%M%S'
        y15s = lib.y15sformat_time(start_up_orig)
        self.assertIsInstance(y15s, str)
        self.assertRegex(y15s, r"\A\d{4}-\d{2}-\d{2}T\d{6}\Z")

    def test_elapsed_time(self):
        td = D_TIMEDELTA.get(self._testMethodName, TD_ZERO)

        start_up_orig = lib.make_start_up_orig()
        et = lib.elapsed_time(start_up_orig - td)
        self.assertEqual(73138, et)

    def test_keycmp_simple(self):
        # b'\xff' * 16
        # int.to_bytes(255, 1, 'big')
        # int.to_bytes(0, 1, 'big')
        keyffff = b'\xff' * KEY_OCTETS
        keyfffe = b'\xff' * (KEY_OCTETS-1) + b'\xfe'
        key7fff = b'\x7f' + b'\xff' * (KEY_OCTETS-1)
        key7ffe = b'\x7f' + b'\xff' * (KEY_OCTETS-2) + b'\xfe'

        key0000 = b'\x00' * KEY_OCTETS
        key0001 = b'\x00' * (KEY_OCTETS-1) + b'\x01'
        key8000 = b'\x80' + b'\x00' * (KEY_OCTETS-1)
        key8001 = b'\x80' + b'\x00' * (KEY_OCTETS-2) + b'\x01'

        self.assertEqual(KEY_OCTETS, 32)
        self.assertEqual(len(keyffff), KEY_OCTETS)
        self.assertEqual(len(keyfffe), KEY_OCTETS)
        self.assertEqual(len(key7fff), KEY_OCTETS)
        self.assertEqual(len(key7ffe), KEY_OCTETS)
        self.assertEqual(len(key0000), KEY_OCTETS)
        self.assertEqual(len(key0001), KEY_OCTETS)
        self.assertEqual(len(key8000), KEY_OCTETS)
        self.assertEqual(len(key8001), KEY_OCTETS)

        # Greater means Red, Less means Green, Eq means White

        self.assertEqual(keycmp(key0000, key0000), 0)   # eq     White
        self.assertGreater(keycmp(key0001, key0000), 0) # + 1    Red
        self.assertGreater(keycmp(key7fff, key0000), 0) # + 7fff Red
        self.assertLess(keycmp(key8000, key0000), 0)    # + 8000 Green
        self.assertLess(keycmp(keyffff, key0000), 0)    # - 1    Green

        self.assertEqual(keycmp(key7fff, key7fff), 0)   # eq
        self.assertGreater(keycmp(key8000, key7fff), 0) # + 1
        self.assertGreater(keycmp(keyfffe, key7fff), 0) # + 7fff
        self.assertLess(keycmp(keyffff, key7fff), 0)    # + 8000
        self.assertLess(keycmp(key7ffe, key7fff), 0)    # -1

        self.assertEqual(keycmp(key8000, key8000), 0)   # eq
        self.assertGreater(keycmp(key8001, key8000), 0) # + 1
        self.assertGreater(keycmp(keyffff, key8000), 0) # + 7fff
        self.assertLess(keycmp(key0000, key8000), 0)    # + 8000
        self.assertLess(keycmp(key7fff, key8000), 0)    # -1

        self.assertEqual(keycmp(keyffff, keyffff), 0)   # eq
        self.assertGreater(keycmp(key0000, keyffff), 0) # + 1
        self.assertGreater(keycmp(key7ffe, keyffff), 0) # + 7fff
        self.assertLess(keycmp(key7fff, keyffff), 0)    # + 8000
        self.assertLess(keycmp(keyfffe, keyffff), 0)    # -1

    def test_keycmp_cross(self):
        key0000 = b'\x00' * KEY_OCTETS
        keyffff = b'\xff' * KEY_OCTETS

        key1fff = b'\x1f' + b'\xff' * (KEY_OCTETS-1)
        key2000 = b'\x20' + b'\x00' * (KEY_OCTETS-1)
        key2001 = b'\x20' + b'\x00' * (KEY_OCTETS-2) + b'\x01'

        key5fff = b'\x5f' + b'\xff' * (KEY_OCTETS-1)
        key6000 = b'\x60' + b'\x00' * (KEY_OCTETS-1)
        key6001 = b'\x60' + b'\x00' * (KEY_OCTETS-2) + b'\x01'

        key9fff = b'\x9f' + b'\xff' * (KEY_OCTETS-1)
        keya000 = b'\xa0' + b'\x00' * (KEY_OCTETS-1)
        keya001 = b'\xa0' + b'\x00' * (KEY_OCTETS-2) + b'\x01'

        keydfff = b'\xdf' + b'\xff' * (KEY_OCTETS-1)
        keye000 = b'\xe0' + b'\x00' * (KEY_OCTETS-1)
        keye001 = b'\xe0' + b'\x00' * (KEY_OCTETS-2) + b'\x01'

        self.assertEqual(KEY_OCTETS, 32)
        self.assertEqual(len(key0000), KEY_OCTETS)
        self.assertEqual(len(keyffff), KEY_OCTETS)
        self.assertEqual(len(key1fff), KEY_OCTETS)
        self.assertEqual(len(key2000), KEY_OCTETS)
        self.assertEqual(len(key2001), KEY_OCTETS)
        self.assertEqual(len(key5fff), KEY_OCTETS)
        self.assertEqual(len(key6000), KEY_OCTETS)
        self.assertEqual(len(key6001), KEY_OCTETS)
        self.assertEqual(len(key9fff), KEY_OCTETS)
        self.assertEqual(len(keya000), KEY_OCTETS)
        self.assertEqual(len(keya001), KEY_OCTETS)
        self.assertEqual(len(keydfff), KEY_OCTETS)
        self.assertEqual(len(keye000), KEY_OCTETS)
        self.assertEqual(len(keye001), KEY_OCTETS)

        # Greater means Red, Less means Green, Eq means White

        self.assertEqual(keycmp(key2000, key2000), 0)   # eq     White
        self.assertGreater(keycmp(key2001, key2000), 0) # + 1    Red
        self.assertGreater(keycmp(key9fff, key2000), 0) # + 7fff Red
        self.assertLess(keycmp(keya000, key2000), 0)    # + 8000 Green
        self.assertLess(keycmp(key1fff, key2000), 0)    # - 1    Green
        self.assertLess(keycmp(keyffff, key2000), 0)    # end    Green
        self.assertLess(keycmp(key0000, key2000), 0)    # zero   Green

        self.assertEqual(keycmp(key6000, key6000), 0)   # eq     White
        self.assertGreater(keycmp(key6001, key6000), 0) # + 1    Red
        self.assertGreater(keycmp(keydfff, key6000), 0) # + 7fff Red
        self.assertLess(keycmp(keye000, key6000), 0)    # + 8000 Green
        self.assertLess(keycmp(key5fff, key6000), 0)    # - 1    Green
        self.assertLess(keycmp(keyffff, key6000), 0)    # end    Green
        self.assertLess(keycmp(key0000, key6000), 0)    # zero   Green

        self.assertEqual(keycmp(keya000, keya000), 0)   # eq     White
        self.assertGreater(keycmp(keya001, keya000), 0) # + 1    Red
        self.assertGreater(keycmp(key1fff, keya000), 0) # + 7fff Red
        self.assertLess(keycmp(key2000, keya000), 0)    # + 8000 Green
        self.assertLess(keycmp(key9fff, keya000), 0)    # - 1    Green
        self.assertGreater(keycmp(keyffff, keya000), 0) # end    Red
        self.assertGreater(keycmp(key0000, keya000), 0) # zero   Red

        self.assertEqual(keycmp(keye000, keye000), 0)   # eq     White
        self.assertGreater(keycmp(keye001, keye000), 0) # + 1    Red
        self.assertGreater(keycmp(key5fff, keye000), 0) # + 7fff Red
        self.assertLess(keycmp(key6000, keye000), 0)    # + 8000 Green
        self.assertLess(keycmp(keydfff, keye000), 0)    # - 1    Green
        self.assertGreater(keycmp(keyffff, keye000), 0) # end    Red
        self.assertGreater(keycmp(key0000, keye000), 0) # zero   Red

if __name__ == '__main__':
    unittest.main()
