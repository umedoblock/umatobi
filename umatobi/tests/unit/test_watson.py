import os, datetime
import sys, shutil
import threading, io, selectors
import unittest
from unittest.mock import call, MagicMock
from umatobi.simulator.sql import SQL

from umatobi.tests import *
from umatobi.simulator.watson import Watson, WatsonOffice
from umatobi.simulator.watson import WatsonOpenOffice, WatsonTCPOffice
from umatobi.lib import *

class Req(object):
    # use self.rfile.readline() in WatsonOffice.handle()
    def makefile(self, mode, rbufsize):
        sheep = {}
        sheep['profess'] = 'I am Client.'
        sheep['num_nodes'] = 333
        self.sheep = sheep
        js_sheep = dict2json(sheep)
        return io.BytesIO(js_sheep.encode('utf-8'))

    def sendall(self, b):
        pass

class WatsonOfficeTestsHandle(WatsonOffice):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

class WatsonOfficeTests(unittest.TestCase):

    def setUp(self):
        self.watson_office_addr = ('localhost', 65530)
        self.start_up_iso8601 = SimulationTime()
        self.log_level = 'INFO'
        self.log_level = 'DEBUG'

        self.watson = Watson(self.watson_office_addr, SIMULATION_SECONDS,
                             self.start_up_iso8601, self.log_level)

    def test_handle(self):
        watson = self.watson
        watson.touch_simulation_db_on_clients()
        watson.simulation_db.access_db()
        clients = tuple(watson.simulation_db.select('clients'))
        watson.simulation_db.close()
        self.assertSequenceEqual([], clients)

        client_address = ('127.0.0.1', 60626)
        server = WatsonTCPOffice(watson)

        request = Req()
        expected_now = SimulationTime()
        with time_machine(expected_now.start_up_orig):
            watson_office = \
                WatsonOfficeTestsHandle(request, client_address, server)
        self.assertTrue(watson_office.to_client)
        self.assertEqual(len(watson_office.server.clients), 1)
        self.assertEqual(request.sheep['num_nodes'], watson_office.server.watson.total_nodes)

        tc = watson_office.to_client
        self.assertFalse('simulation_dir_path' in tc)
        self.assertFalse('simulation_db_path' in tc)
        self.assertFalse('simulation_schema_path' in tc)

        self.assertEqual(tc['client_id'], 1)
        self.assertEqual(tc['start_up_iso8601'], \
                         watson.start_up_iso8601.get_iso8601())
        self.assertEqual(tc['node_index'], 1)
        self.assertEqual(tc['log_level'], watson.log_level)

        clients = tuple(watson_office.server.simulation_db.select('clients'))
        self.assertEqual(1, len(clients))

        d_client = dict(clients[0])
        self.assertEqual(d_client['id'], 1)
        c_a = client_address
        expected_addr = f'{c_a[0]}:{c_a[1]}'
        self.assertEqual(d_client['addr'], expected_addr)
        self.assertEqual(d_client['consult_iso8601'], \
                         expected_now.get_iso8601())
        self.assertEqual(d_client['thanks_iso8601'], None)
        self.assertEqual(d_client['num_nodes'], request.sheep['num_nodes'])
        self.assertEqual(d_client['node_index'], 1)
        self.assertEqual(d_client['log_level'], watson.log_level)

        server.server_close()

class WatsonTests(unittest.TestCase):
    def setUp(self):
        self.watson_office_addr = ('localhost', 65530)
        self.log_level = 'INFO'
        self.start_up_iso8601 = SimulationTime()

        self.watson = Watson(self.watson_office_addr, SIMULATION_SECONDS,
                             self.start_up_iso8601, self.log_level)

        self.outsider_db = SQL(db_path=self.watson.simulation_db_path,
                               schema_path=self.watson.simulation_schema_path)

    def tearDown(self):
        # delete dbs, logs...
        shutil.rmtree(self.watson.simulation_dir_path, ignore_errors=True)

    def test_watson_basic(self):
        watson = self.watson
        expected_simulation_dir_path = \
                get_simulation_dir_path(self.start_up_iso8601)
        expected_simulation_db_path = \
                get_simulation_db_path(self.start_up_iso8601)
        expected_simulation_schema_path = \
                get_simulation_schema_path(self.start_up_iso8601)

        self.assertTrue(os.path.isdir(watson.simulation_dir_path))
        self.assertEqual(watson.watson_office_addr, self.watson_office_addr)
        self.assertEqual(watson.simulation_dir_path, expected_simulation_dir_path)
        self.assertEqual(watson.simulation_db_path, expected_simulation_db_path)
        self.assertEqual(watson.simulation_schema_path, expected_simulation_schema_path)
        self.assertEqual(watson.total_nodes, 0)

    @patch('umatobi.simulator.watson.WatsonOpenOffice')
    def test_open_office(self, mock_WatsonOpenOffice):
        # woo stands for WatsonOpenOffice.
        watson = self.watson

        mock_WatsonOpenOffice.assert_not_called()
        woo = watson.open_office()
        mock_WatsonOpenOffice.assert_called()
        self.assertEqual(woo, watson.watson_open_office)

        watson.watson_open_office.start.assert_called()
        watson.watson_open_office.in_serve_forever.wait.assert_called()

    @patch('time.sleep')
    def test_watson_start(self, mock_sleep):
        watson = self.watson
        # 以下では，watson.start() の emulate

        watson.touch_simulation_db_on_clients()
        watson_open_office = watson.open_office()

        mock_sleep.assert_not_called()
        watson.relaxing()
        mock_sleep.assert_called()

        watson.release_clients()
        watson.watson_tcp_office.shutdown() # heavy
        watson._wait_client_db()

        watson.simulation_db.access_db()
        watson._merge_db_to_simulation_db()
        watson._create_simulation_table()
        watson._construct_simulation_table()
        watson.simulation_db.close()

    def test__create_simulation_db(self):
        watson = self.watson
        watson.touch_simulation_db_on_clients()
        watson.simulation_db.access_db()

        outsider_db = self.outsider_db
        outsider_db.access_db()

        before_tables = set(outsider_db.get_table_names())
       #print('before_tables =', before_tables)

        # create 'simulation' table
        watson._create_simulation_table()

        after_tables = set(outsider_db.get_table_names())
       #print('after_tables =', after_tables)

        self.assertEqual(after_tables - before_tables, set(('simulation',)))

        watson.simulation_db.remove_db()

    def test__construct_simulation_table(self):
        watson = self.watson
        watson.total_nodes = total_nodes = 100
        watson.touch_simulation_db()
        watson.simulation_db.access_db()
        watson._create_simulation_table()

        outsider_db = self.outsider_db
        outsider_db.access_db()

        n_clients = 30
        watson.watson_tcp_office = MagicMock(clients=[None] * n_clients)

        # first check
        selected_rows = outsider_db.select('simulation')
        self.assertEqual(len(selected_rows), 0)

        # test start, watson._construct_simulation_table()
        d_simulation = watson._construct_simulation_table()
        expected_rows = tuple(d_simulation.values())

        selected_rows = outsider_db.select('simulation')
        self.assertEqual(len(selected_rows), 1)
       #print(tuple(simulation_rows[0]))
        self.assertEqual(tuple(selected_rows[0]), expected_rows)

        watson.simulation_db.remove_db()

####if hasattr(selectors, 'PollSelector'):
####  # _ServerSelector = selectors.PollSelector
####  # _ServerSelector = <class 'selectors.PollSelector'>
####    patch_arg = 'selectors.PollSelector.select'
####else:
####  # _ServerSelector = selectors.SelectSelector
####    patch_arg = 'selectors.SelectSelector.select'

####@patch(patch_arg, return_value=False)
####@patch('time.sleep')
####def test_watson_start2(self, mock_sleep, mock_selector):
####    watson = self.watson
####    # 以下では，watson.start() の emulate

####    watson.touch_simulation_db_on_clients()
####    watson_open_office = watson.open_office()

####    mock_sleep.assert_not_called()
####    watson.relaxing()
####    mock_sleep.assert_called()

####    watson.release_clients()
####    watson.watson_tcp_office.shutdown() # heavy
####    watson._wait_client_db()

####    watson.simulation_db.access_db()
####    watson._merge_db_to_simulation_db()
####    watson._construct_simulation_table()
####    watson.simulation_db.close()

if __name__ == '__main__':
    unittest.main()
