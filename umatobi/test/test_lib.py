import os, sys, datetime, shutil
import unittest

from umatobi.test import *
from umatobi import lib
from umatobi.lib import make_logger

_datetime_datetime = datetime.datetime
_now = datetime.datetime.now

class mock_datetime(datetime.datetime):
    NEED_MOCK = False
    count = 0
    now_buf = None

    @staticmethod
    def now():
        if not mock_datetime.NEED_MOCK:
            return _now()
        else:
            if mock_datetime.count == 0:
                mock_datetime.count += 1
                mock_datetime.now_buf = _now()
                return mock_datetime.now_buf
            else:
                return mock_datetime.now_buf + \
                       datetime.timedelta(0, 73, 138770)

class LibTests(unittest.TestCase):

    def test_SIMULATION_DIR(self):
        self.assertEqual('umatobi-simulation-test', SIMULATION_DIR)

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
        self.assertEqual('umatobi-simulation-test/test_logger.log', tlogger.log_path)

        tlogger = make_logger(log_dir=SIMULATION_DIR, name='test_logger', id_=888, level="INFO")
        self.assertEqual('umatobi-simulation-test/test_logger.888.log', tlogger.log_path)

    def test_make_start_up_orig(self):
        start_up_orig = lib.make_start_up_orig()
        self.assertIsInstance(start_up_orig, datetime.datetime)

    def test_y15sformat_time(self):
        start_up_orig = lib.make_start_up_orig()
        # Y15S_FORMAT='%Y-%m-%dT%H%M%S'
        y15s = lib.y15sformat_time(start_up_orig)
        self.assertIsInstance(y15s, str)
        self.assertRegex(y15s, r"\A\d{4}-\d{2}-\d{2}T\d{6}\Z")

    def test_elapsed_time(self):
        datetime.datetime = mock_datetime
        mock_datetime.NEED_MOCK = True

        start_up_orig = lib.make_start_up_orig()
        et = lib.elapsed_time(start_up_orig)
        self.assertEqual(73138, et)

        mock_datetime.NEED_MOCK = False
        datetime.datetime = _datetime_datetime

if __name__ == '__main__':
    unittest.main()
