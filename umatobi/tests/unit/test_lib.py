import os, sys, datetime, shutil
import unittest

from umatobi.tests import *
from umatobi.log import logger, make_logger
from umatobi import lib

class LibTests(unittest.TestCase):

    def test_get_table_columns(self):
        expected_items = {
            'simulation': (
                'watson_office_addr', 'simulation_ms', 'title',
                'memo', 'version', 'n_clients', 'total_nodes'
            ),
            'nodes': (
                'id', 'office_addr', 'keyid', 'key', 'rad', 'x', 'y', 'status'
            ),
            'clients': (
                'id', 'host', 'port', 'joined', 'log_level',
                'num_nodes', 'node_index'
            ),
            'growings': ( 'id', 'elapsed_time', 'pickle')

        }

        db = lib.get_db_from_schema()
        self.assertSequenceEqual(db.sections(), tuple(expected_items.keys()))

        for section in db.sections():
            self.assertSequenceEqual(tuple(db[section].keys()), tuple(expected_items[section]))

    def test_dict2json_and_json2dict(self):
        d = {
            'port': 1000,
            'host': 'localhost',
            'key': '0x' + '1234567890abcedf' * 4,
        }

        self.assertIsInstance(d, dict)
        j = lib.dict2json(d)
        self.assertIsInstance(j, str)
        d2 = lib.json2dict(j)
        self.assertIsInstance(d2, dict)
        self.assertNotEqual(id(d2), id(d))
        self.assertEqual(d2, d)

    def test_dict2bytes_and_bytes2dict(self):
        d = {
            'port': 1000,
            'host': 'localhost',
            'key': '0x' + '1234567890abcedf' * 4,
        }

        self.assertIsInstance(d, dict)
        b = lib.dict2bytes(d)
        self.assertIsInstance(b, bytes)
        d2 = lib.bytes2dict(b)
        self.assertIsInstance(d2, dict)
        self.assertNotEqual(id(d2), id(d))
        self.assertEqual(d2, d)

    def test_SIMULATION_DIR(self):
        self.assertEqual('tests/umatobi-simulation', SIMULATION_DIR)

    def test_master_hand(self):
        y15s_time = lib.current_y15sformat_time()
        self.assertEqual(lib.get_master_hand(y15s_time), f"{y15s_time}/{MASTER_HAND}")

    def test_master_hand_path(self):
        y15s_time = lib.current_y15sformat_time()
        self.assertEqual(lib.get_master_hand_path(SIMULATION_DIR, y15s_time), f"tests/umatobi-simulation/{y15s_time}/{MASTER_HAND}")

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
        self.assertEqual('tests/umatobi-simulation/test_logger.log', tlogger.log_path)

        tlogger = make_logger(log_dir=SIMULATION_DIR, name='test_logger', id_=888, level="INFO")
        self.assertEqual('tests/umatobi-simulation/test_logger.888.log', tlogger.log_path)

    def test_make_start_up_orig(self):
        start_up_orig = lib.make_start_up_orig()
        self.assertIsInstance(start_up_orig, datetime.datetime)

    def test_make_start_up_orig_with_time_machine(self):
        start_up_orig = lib.make_start_up_orig()
        years_1000 = datetime.timedelta(days=1000*365)

        past = start_up_orig - years_1000
        current = start_up_orig
        future = start_up_orig + years_1000

        with time_machine(past):
            self.assertEqual(lib.make_start_up_orig(), past)

        with time_machine(current):
            self.assertEqual(lib.make_start_up_orig(), current)

        with time_machine(future):
            self.assertEqual(lib.make_start_up_orig(), future)

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

    def mocked_datetime_now(mocked_datetime=None):
        if not mocked_datetime:
            return mocked_datetime
        else:
            return datetime.datetime.now()

    def test_mock_datetime_now(self):
        manipulated_datetime = datetime.datetime(2011, 11, 11, 11, 11, 11, 111111)
        with time_machine(manipulated_datetime):
            self.assertEqual(lib.datetime_now(), manipulated_datetime)

if __name__ == '__main__':
    unittest.main()
