import sys, datetime
import unittest

from umatobi import lib

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
