# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import os, sys, re, shutil, pathlib, pickle
from datetime import datetime
import unittest
from unittest.mock import patch, MagicMock

# from umatobi.constants import *
from umatobi.tests import *
from umatobi.tests.constants import *
# from umatobi.lib import *

from umatobi.lib.simulation_time import *

class SimulationTimeTests(unittest.TestCase):

    def setUp(self):
        self.simulation_dir_path = \
            os.path.join(SIMULATION_ROOT_PATH, UMATOBI_SIMULATION_DIR_PATH)
        self.simulation_time = SimulationTime()
        self.path_maker = PathMaker(self.simulation_time)

    def tearDown(self):
        shutil.rmtree(self.path_maker.get_simulation_schema_path(), ignore_errors=True)

    def test_time_machine_now(self):
        start_up_orig = SimulationTime.now()

        with time_machine(start_up_orig):
            simulation_time = SimulationTime()
        self.assertIsInstance(simulation_time.start_up_orig,
                              datetime)
        self.assertEqual(simulation_time.start_up_orig, start_up_orig)

    def test_mock_datetime_now(self):
        manipulated_datetime = datetime(2011, 11, 11, 11, 11, 11, 111111)
        with time_machine(manipulated_datetime):
            self.assertEqual(SimulationTime.now(), manipulated_datetime)

    def test_iso8601_to_time(self):
        isoformat = '2011-11-11T11:11:11.111111'
        self.assertEqual(SimulationTime.iso8601_to_time(isoformat), SimulationTime(datetime(2011, 11, 11, 11, 11, 11, 111111)))

    def test_time_to_iso8601(self):
        start_up_orig = datetime(2011, 11, 11, 11, 11, 11, 111111)
        with time_machine(start_up_orig):
            self.assertEqual(SimulationTime.time_to_iso8601(SimulationTime()), '2011-11-11T11:11:11.111111')

    def test_y15s_to_time(self):
        pass

    def test_time_to_y15s(self):
        # Y15S_FORMAT='%Y-%m-%dT%H%M%S'
        simulation_time = self.simulation_time
        y15s = SimulationTime.time_to_y15s(simulation_time)
        self.assertIsInstance(y15s, str)
        self.assertRegex(y15s, r"\A\d{4}-\d{2}-\d{2}T\d{6}\Z")

    def test_time_to_y15s_2(self):
        # Y15S_FORMAT='%Y-%m-%dT%H%M%S'
        y15s = SimulationTime.time_to_y15s(SimulationTime())
        self.assertIsInstance(y15s, str)
        self.assertRegex(y15s, r"\A\d{4}-\d{2}-\d{2}T\d{6}\Z")

    def test___init__(self):
        self.assertIsInstance(self.simulation_time.start_up_orig, datetime)

    def test___str__(self):
        pass

    def test___repr__(self):
        pass

    def test___eq__(self):
        pass

    def test_get_iso8601(self):
        self.assertRegex(self.simulation_time.get_iso8601(), RE_ISO8601)

    def test_get_y15s(self):
        self.assertRegex(self.simulation_time.get_y15s(), RE_Y15S)

    def test_passed_seconds(self):
        simulation_time = SimulationTime()
        passed_seconds = 123.456
        passed_time = timedelta(seconds=passed_seconds)

        with time_machine(simulation_time.start_up_orig + passed_time):
            self.assertEqual(simulation_time.passed_seconds(),
                             passed_seconds)

    def test_passed_ms(self):
        mili555 = timedelta(milliseconds=555)
        simulation_time = SimulationTime()
        start_up_orig = simulation_time.start_up_orig
        with time_machine(start_up_orig + mili555):
            passed_ms = simulation_time.passed_ms(SimulationTime().start_up_orig)
        self.assertEqual(passed_ms, 555)

    def test_make_start_up_orig_with_time_machine(self):
        start_up_orig = self.simulation_time.start_up_orig

        years_1000 = timedelta(days=1000*365)
        past = start_up_orig - years_1000
        current = start_up_orig
        future = start_up_orig + years_1000

        with time_machine(past):
            self.assertEqual(SimulationTime().start_up_orig, past)

        with time_machine(current):
            self.assertEqual(SimulationTime().start_up_orig, current)

        with time_machine(future):
            self.assertEqual(SimulationTime().start_up_orig, future)

class PathMakerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.simulation_time = SimulationTime()
        cls.path_maker = PathMaker(cls.simulation_time)

    @classmethod
    def tearDownClass(cls):
        pass

    def assert_client_db_path(self, client_db_path):
        self.assertRegex(client_db_path, RE_CLIENT_N_DB)
        self.assertNotRegex(client_db_path, ATAT_N)

    def assert_simulation_schema_path(self, inspected_path):
        self.assert_simulation_dir_path(inspected_path)
        self.assertRegex(inspected_path, f'{SIMULATION_SCHEMA}$')

    def assert_simulation_dir_path(self, dir_path):
        self.assertTrue(os.path.isdir(os.path.dirname(dir_path)))
        self.assertNotRegex(dir_path,
                            ATAT_SIMULATION_TIME)
        self.assertRegex(dir_path, RE_Y15S)

    def setUp(self):
        self.path_maker = PathMakerTests.path_maker

#   def tearDown(self):
#       cleanup_paths = []
#       cleanup_paths.append(self.path_maker.get_simulation_schema_path())
#       cleanup_paths.append(self.path_maker.get_master_palm_txt_path())
#       for cleanup_path in cleanup_paths:
#           p = pathlib.Path(cleanup_path)
#           if p.is_file():
#               p.unlink()

    def test___eq__(self):
        iso8601 = SimulationTime().get_iso8601()
        simulation_time_0 = SimulationTime(iso8601)
        simulation_time_1 = SimulationTime(iso8601)
        path_maker_0 = PathMaker(simulation_time_0)
        path_maker_1 = PathMaker(simulation_time_1)

        self.assertEqual(path_maker_0, path_maker_1)
        self.assertEqual(simulation_time_0, simulation_time_1)
        self.assertNotEqual(id(path_maker_0.simulation_time),
                            id(path_maker_1.simulation_time))

    def test___init__(self):
        path_maker = self.path_maker
        self.assertIsInstance(path_maker, PathMaker)
        self.assertEqual(path_maker.simulation_time, \
                         PathMakerTests.simulation_time)

    def test_get_client_db_path(self):
        path_maker = self.path_maker
        client_id = 8
        client_db_path = path_maker.get_client_db_path(client_id)

        self.assertEqual(client_db_path,
                os.path.join(
                    re.sub(ATAT_SIMULATION_TIME,
                    path_maker.simulation_time.get_y15s(),
                    UMATOBI_SIMULATION_DIR_PATH), 'client.8.db'))

        client_id = 88888
        client_db_path = path_maker.get_client_db_path(client_id)
        self.assert_client_db_path(client_db_path)

    # SimulationTime.Y15S_FORMAT='%Y-%m-%dT%H%M%S'
    def test_get_simulation_dir_path(self):
        path_maker = self.path_maker
        simulation_dir_path = path_maker.get_simulation_dir_path()
        self.assert_simulation_dir_path(simulation_dir_path)

    @patch('os.path.join')
    def test_get_simulation_schema_path(self, mock_join):
        path_maker = self.path_maker

        simulation_schema_path = path_maker.get_simulation_schema_path()

        mock_join.assert_called_once_with(path_maker.get_simulation_dir_path(),
                                          SIMULATION_SCHEMA)

    def test_get_module_path(self):
        path_maker = self.path_maker
        self.assertNotRegex(path_maker.get_module_path(), '/umatobi/tests/')
        self.assertEqual(path_maker.get_module_path(), UMATOBI_MODULE_PATH)

    @patch('os.makedirs')
    @patch('os.path.isfile', return_value=False)
    @patch('os.path.isdir', return_value=False)
    @patch('shutil.copyfile')
    def test_set_simulation_schema(self, mock_copyfile, mock_isdir, mock_isfile, mock_makedirs):
        path_maker = self.path_maker
        simulation_dir_path = path_maker.get_simulation_dir_path()
        simulation_schema_path = path_maker.get_simulation_schema_path()

        with self.assertLogs('umatobi', level='INFO') as cm:
            simulation_schema_path = path_maker.set_simulation_schema()

        self.assertEqual(cm.output[0], f"INFO:umatobi:os.makedirs('{simulation_dir_path}')")
        self.assertEqual(cm.output[1],
                f"INFO:umatobi:shutil.copyfile(SIMULATION_SCHEMA_PATH={SIMULATION_SCHEMA_PATH}, simulation_schema_path={simulation_schema_path})")
        mock_isfile.assert_called_once_with(path_maker.get_simulation_schema_path())
        mock_isdir.assert_called_once_with(path_maker.get_simulation_dir_path())
        mock_makedirs.assert_called_once_with(path_maker.get_simulation_dir_path(), exist_ok=True)
        mock_copyfile.assert_called_once_with(SIMULATION_SCHEMA_PATH, simulation_schema_path)

    @patch('os.path.isfile', return_value=True)
    def test_set_simulation_schema_path(self, mock_isfile):
        path_maker = self.path_maker

        try:
            with self.assertLogs('umatobi', level='INFO') as cm:
                simulation_schema_path = path_maker.set_simulation_schema()
        except AssertionError as err:
            self.assertEqual(err.args[0], 'no logs of level INFO or higher triggered on umatobi')

        mock_isfile.assert_called_once_with(simulation_schema_path)

    def test_get_master_palm_txt_path(self):
        path_maker = self.path_maker
        self.assertEqual(
            path_maker.get_master_palm_txt_path(),
            os.path.join(SIMULATION_ROOT_PATH,
                         path_maker.simulation_time.get_y15s(),
                         MASTER_PALM_TXT))

    @patch('os.path.isdir', return_value=False)
    @patch('os.makedirs')
    def test_make_simulation_dir(self, mock_makedirs, mock_isdir):
        path_maker = self.path_maker
        simulation_dir_path = path_maker.get_simulation_dir_path()

        mock_isdir.assert_not_called()
        with self.assertLogs('umatobi', level='INFO') as cm:
            path_maker.make_simulation_dir()
        self.assertRegex(cm.output[0], fr"^INFO:umatobi:os.makedirs\('/.+/{RE_Y15S}'\)$")
        self.assertEqual(cm.output[0], f"INFO:umatobi:os.makedirs('{simulation_dir_path}')")
        mock_isdir.assert_called_once()
        mock_makedirs.assert_called_with(simulation_dir_path, exist_ok=True)

    @patch('os.path.isdir', return_value=True)
    @patch('os.makedirs')
    def test_make_simulation_dir_path(self, mock_makedirs, mock_isdir):
        path_maker = self.path_maker
        simulation_dir_path = path_maker.get_simulation_dir_path()

        mock_isdir.assert_not_called()

        path_maker.make_simulation_dir()

        mock_isdir.assert_called_once()
        mock_makedirs.assert_not_called()

if __name__ == '__main__':
    unittest.main()
