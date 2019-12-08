# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

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

class WatsonOpenOfficeTests(unittest.TestCase):

    def test___init__(self):
        pass

    def test_run(self):
        pass

class WatsonTCPOfficeTests(unittest.TestCase):

    def test___init__(self):
        pass

    def test__determine_office_addr(self):
        pass

    def test_shutdown_request(self):
        pass

class WatsonOfficeTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.start_up_orig = SimulationTime()

    @classmethod
    def tearDownClass(cls):
        cls.start_up_orig = None

    def setUp(self):
        self.watson_office_addr = ('localhost', 65530)
        self.start_up_orig = WatsonOfficeTests.start_up_orig
        self.log_level = 'DEBUG'
        self.log_level = 'INFO'

        self.watson = Watson(self.watson_office_addr, SIMULATION_SECONDS,
                             self.start_up_orig, self.log_level)

    def test___init__(self):
        watson = self.watson
        watson.touch_simulation_db_on_clients()
        watson.simulation_db.access_db()
        clients = tuple(watson.simulation_db.select('clients'))
        watson.simulation_db.close()
        self.assertSequenceEqual(clients, [])

        client_address = ('127.0.0.1', 60626)
        server = WatsonTCPOffice(watson)

        request = Req('I am Client.', 333)
        self.assertEqual(request.sheep['profess'], 'I am Client.')
        self.assertEqual(request.sheep['num_nodes'], 333)

        with self.assertRaises(AttributeError) as cm:
            request._written
        the_exception = cm.exception
        self.assertEqual(the_exception.args[0],
                       "'Req' object has no attribute '_written'")

        expected_now = SimulationTime()
        with time_machine(expected_now.start_up_orig):
            # WatsonOffice() indide calls
            # setup(), handle() and finish()
            watson_office = WatsonOffice(request, client_address, server)

        # __init__() ######################################################
        self.assertEqual(watson_office.request, request)
        self.assertEqual(watson_office.client_address, client_address)
        self.assertEqual(watson_office.server, server)

        # setup() #########################################################
        self.assertEqual(watson_office.professed, 'I am Client.')
        self.assertEqual(watson_office.num_nodes, 333)

        # handle() ########################################################
        # profess 'I am Client.'
        self.assertEqual(watson_office.consult_orig,
                         expected_now)
        self.assertEqual(watson_office.client_id, 0)
        self.assertEqual(len(watson_office.server.clients), 1)
        self.assertEqual(watson_office.node_index, 0)
        self.assertEqual(watson_office.server.watson.total_nodes, 333)
        self.assertIsInstance(watson_office.client_reply, bytes)

        # outsider ########################################################
        outsider_db = SQL(db_path=watson.simulation_db_path,
                          schema_path=watson.simulation_schema_path)
        outsider_db.access_db()

        # insert_client_record() in handle() ##############################
        clients = tuple(outsider_db.select('clients'))
        self.assertEqual(len(clients), 1)

        d_client = dict(clients[0])
        self.assertEqual(d_client['id'], 0)

        c_a = client_address
        expected_addr = f'{c_a[0]}:{c_a[1]}'
        self.assertEqual(d_client['addr'], expected_addr)
        self.assertEqual(d_client['consult_iso8601'], \
                         expected_now.get_iso8601())
        self.assertEqual(d_client['thanks_iso8601'], None)
        self.assertEqual(d_client['num_nodes'], request.sheep['num_nodes'])
        self.assertEqual(d_client['node_index'], 0)
        self.assertEqual(d_client['log_level'], watson.log_level)

        # make_client_reply() in handle() #################################
        dcr = watson_office.d_client_reply
        set_dcr = set(dcr)
        never_contain = set(('simulation_dir_path',
                             'simulation_db_path',
                             'simulation_schema_path'))
        self.assertFalse(set_dcr & never_contain)

        self.assertEqual(dcr['client_id'], 0)
        self.assertEqual(dcr['start_up_iso8601'], str(watson.start_up_orig))
        self.assertEqual(dcr['node_index'], watson_office.node_index)
        self.assertEqual(dcr['log_level'], watson.log_level)

        self.assertIsInstance(watson_office.client_reply, bytes)
        self.assertEqual(watson_office.client_reply, dict2bytes(dcr))

        # finish() ########################################################
        self.assertEqual(request._written,
                         watson_office.client_reply)

        # cleanup #########################################################
        server.server_close()

    def test_setup(self):
        pass

    def test_handle(self):
        pass

    def test_finish(self):
        pass

    def test_make_client_record(self):
        pass

    def test_insert_client_record(self):
        pass

    def test_make_client_reply(self):
      # with self.assertRaises(AttributeError) as cm:
      #     watson_office.d_client_reply
      # the_exception = cm.exception
      # self.assertEqual(the_exception.args[0], '')
        pass

    def test_byebye(self):
        pass

class WatsonTests(unittest.TestCase):

    def setUp(self):
        self.watson_office_addr = ('localhost', 65530)
        self.log_level = 'INFO'
        self.start_up_orig = SimulationTime()

        self.watson = Watson(self.watson_office_addr, SIMULATION_SECONDS,
                             self.start_up_orig, self.log_level)

        self.outsider_db = SQL(db_path=self.watson.simulation_db_path,
                               schema_path=self.watson.simulation_schema_path)

    def tearDown(self):
        # delete dbs, logs...
        shutil.rmtree(self.watson.simulation_dir_path, ignore_errors=True)

    def test___str__(self):
        pass


    def test___init__(self):
        watson = self.watson
        expected_simulation_dir_path = \
                watson.path_maker.get_simulation_dir_path()
        expected_simulation_db_path = \
                watson.path_maker.get_simulation_db_path()
        expected_simulation_schema_path = \
                watson.path_maker.get_simulation_schema_path()

        self.assertTrue(os.path.isdir(watson.simulation_dir_path))
        self.assertEqual(watson.watson_office_addr, self.watson_office_addr)
        self.assertEqual(watson.simulation_dir_path, expected_simulation_dir_path)
        self.assertEqual(watson.simulation_db_path, expected_simulation_db_path)
        self.assertEqual(watson.simulation_schema_path, expected_simulation_schema_path)
        self.assertEqual(watson.total_nodes, 0)

    @patch('time.sleep')
    def test_run(self, mock_sleep):
        watson = self.watson
        watson.run()

    @patch('time.sleep')
    def test_start(self, mock_sleep):
        watson = self.watson
        # 以下では，watson.start(), つまり、 run() の emulate

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

    def test_touch_simulation_db_on_clients(self):
        pass

    def test_touch_simulation_db(self):
        pass

    def test_touch_clients_table(self):
        pass

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
    def test_relaxing(self, mock_sleep):
        watson = self.watson

        expected_relaxing_seconds = 23.456
        passed_seconds = watson.simulation_seconds - expected_relaxing_seconds
        with patch.object(watson.start_up_orig, 'passed_seconds',
                          return_value=passed_seconds):
            watson.relaxing()
        mock_sleep.assert_called_with(expected_relaxing_seconds)

    def test_release_clients(self):
        pass

    def test__wait_client_db(self):
        pass

    def test__merge_db_to_simulation_db(self):
        pass

    def test__create_simulation_table(self):
        watson = self.watson
        watson.touch_simulation_db_on_clients()
        watson.simulation_db.access_db()

        outsider_db = self.outsider_db
        outsider_db.access_db()

        before_tables = set(outsider_db.get_table_names())

        # create 'simulation' table
        watson._create_simulation_table()

        after_tables = set(outsider_db.get_table_names())

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

    def test_join(self):
        pass

class Req(object):

    def __init__(self, profess, num_nodes):
        self.sheep = {
            'profess': profess,
            'num_nodes': num_nodes,
        }

    # use self.rfile.readline() in WatsonOffice.handle()
    def makefile(self, mode, rbufsize):
        js_sheep = dict2json(self.sheep)
        return io.BytesIO(js_sheep.encode('utf-8'))

    def sendall(self, b):
        self._written = b

if __name__ == '__main__':
    unittest.main()
