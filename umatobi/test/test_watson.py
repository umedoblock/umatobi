import os, datetime
import sys, shutil
import threading, io
import unittest

from umatobi.test import *
from umatobi.simulator.watson import Watson, WatsonOffice
from umatobi.simulator.watson import WatsonOpenOffice, WatsonTCPOffice
from umatobi import lib

class WatsonTests(unittest.TestCase):
    def setUp(self):
        self.watson_office_addr = ('localhost', 65530)
        simulation_dir = os.path.join(".", SIMULATION_DIR)
        self.log_level = 'INFO'
        self.start_up_orig = lib.make_start_up_orig()
        start_up_time = lib.y15sformat_time(self.start_up_orig)
        dir_name = os.path.join(simulation_dir, start_up_time)
        self.dir_name = dir_name

        td = D_TIMEDELTA.get(self._testMethodName, TD_ZERO)
        self.watson = Watson(self.watson_office_addr, SIMULATION_SECONDS,
                        self.start_up_orig - td,
                        self.dir_name, self.log_level)

    def tearDown(self):
        # delete dbs, logs...
        shutil.rmtree(self.watson.dir_name, ignore_errors=True)

    def test_watson_basic(self):
        watson = self.watson

        expected_dir = os.path.join('.', SIMULATION_DIR, watson.start_up_time)
        expected_path = os.path.join('.', SIMULATION_DIR, watson.start_up_time, SIMULATION_DB)

        self.assertEqual(self.watson_office_addr, watson.watson_office_addr)
        self.assertEqual(expected_dir, watson.dir_name)
        self.assertEqual(expected_path, watson.simulation_db_path)
        self.assertEqual(0, watson.total_nodes)

    def test_watson_start(self):
        watson = self.watson
        # 以下では，watson.start() の emulate

        watson.touch_simulation_db_on_clients()
        watson_open_office = watson.open_office()

        watson.relaxing()

        watson.release_clients()
        watson.watson_tcp_office.shutdown()
        watson._wait_client_db()

        watson.simulation_db.access_db()
        watson._merge_db_to_simulation_db()
        watson._construct_simulation_table()
        watson.simulation_db.close()

class Req(object):
    # use self.rfile.readline() in WatsonOffice.handle()
    def makefile(self, mode, rbufsize):
        sheep = {}
        sheep['profess'] = 'I am Client.'
        sheep['num_nodes'] = 111111
        self.sheep = sheep
        js_sheep = lib.dict2json(sheep)
        return io.BytesIO(js_sheep.encode('utf-8'))

    def sendall(self, b):
        pass

class WatsonOfficeTestsHandle(WatsonOffice):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

class WatsonOfficeTests(unittest.TestCase):

    def setUp(self):
        self.watson_office_addr = ('localhost', 65530)
        simulation_dir = os.path.join(".", SIMULATION_DIR)
        self.log_level = 'INFO'
        self.log_level = 'DEBUG'
        self.start_up_orig = lib.make_start_up_orig()
        start_up_time = lib.y15sformat_time(self.start_up_orig)
        dir_name = os.path.join(simulation_dir, start_up_time)
        self.dir_name = dir_name

        td = D_TIMEDELTA.get(self._testMethodName, TD_ZERO)
        self.watson = Watson(self.watson_office_addr, SIMULATION_SECONDS,
                        self.start_up_orig - td,
                        self.dir_name, self.log_level)

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
        watson_office = \
            WatsonOfficeTestsHandle(request, client_address, server)
        self.assertTrue(watson_office.to_client)
        self.assertEqual(1, len(watson_office.server.clients))
        self.assertEqual(request.sheep['num_nodes'], watson_office.server.watson.total_nodes)

        tc = watson_office.to_client
        self.assertEqual(watson.dir_name, tc['dir_name'])
        self.assertEqual(1, tc['client_id'])
        self.assertEqual(watson.start_up_time, tc['start_up_time'])
        self.assertEqual(1, tc['node_index'])
        self.assertEqual(watson.log_level, tc['log_level'])

        clients = tuple(watson_office.server.simulation_db.select('clients'))
        self.assertEqual(1, len(clients))

        d_client = dict(clients[0])
        self.assertEqual(1, d_client['id'])
        self.assertEqual(client_address[0], d_client['host'])
        self.assertEqual(client_address[1], d_client['port'])
        self.assertEqual(1, d_client['node_index'])
      # self.assertEqual(12, d_client['joined'])
        self.assertEqual(watson.log_level, d_client['log_level'])
        self.assertEqual(request.sheep['num_nodes'], d_client['num_nodes'])

if __name__ == '__main__':
    unittest.main()
