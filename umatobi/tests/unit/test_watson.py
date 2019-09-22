import os, datetime
import sys, shutil
import threading, io
import unittest

from umatobi.tests import *
from umatobi.simulator.watson import Watson, WatsonOffice
from umatobi.simulator.watson import WatsonOpenOffice, WatsonTCPOffice
from umatobi.lib import *

class WatsonTests(unittest.TestCase):
    def setUp(self):
        self.watson_office_addr = ('localhost', 65530)
        self.log_level = 'INFO'
        self.simulation_time = SimulationTime()

        td = D_TIMEDELTA.get(self._testMethodName, TD_ZERO)
        self.watson = Watson(self.watson_office_addr, SIMULATION_SECONDS,
                             self.simulation_time, self.log_level)

    def tearDown(self):
        # delete dbs, logs...
        shutil.rmtree(self.watson.simulation_dir_path, ignore_errors=True)

    def test_watson_basic(self):
        watson = self.watson
        expected_simulation_dir_path = \
                get_simulation_dir_path(self.simulation_time)
        expected_simulation_db_path = \
                get_simulation_db_path(self.simulation_time)
        expected_simulation_schema_path = \
                get_simulation_schema_path(self.simulation_time)

        self.assertTrue(os.path.isdir(watson.simulation_dir_path))
        self.assertEqual(watson.watson_office_addr, self.watson_office_addr)
        self.assertEqual(watson.simulation_dir_path, expected_simulation_dir_path)
        self.assertEqual(watson.simulation_db_path, expected_simulation_db_path)
        self.assertEqual(watson.simulation_schema_path, expected_simulation_schema_path)
        self.assertEqual(watson.total_nodes, 0)

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
        self.simulation_time = SimulationTime()
        self.log_level = 'INFO'
        self.log_level = 'DEBUG'

        self.watson = Watson(self.watson_office_addr, SIMULATION_SECONDS,
                             self.simulation_time, self.log_level)

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
        self.assertFalse('simulation_dir_path' in tc)
        self.assertFalse('simulation_db_path' in tc)
        self.assertFalse('simulation_schema_path' in tc)
        self.assertFalse('simulation_time' in tc)
        self.assertEqual(tc['client_id'], 1)
        self.assertEqual(tc['iso8601'], watson.simulation_time.get_iso8601())
        self.assertEqual(tc['node_index'], 1)
        self.assertEqual(tc['log_level'], watson.log_level)

        clients = tuple(watson_office.server.simulation_db.select('clients'))
        self.assertEqual(1, len(clients))

        d_client = dict(clients[0])
        self.assertEqual(d_client['id'], 1)
        self.assertEqual(d_client['host'], client_address[0])
        self.assertEqual(d_client['port'], client_address[1])
        self.assertEqual(d_client['node_index'], 1)
      # self.assertEqual(d_client['joined'], 12)
        self.assertEqual(d_client['log_level'], watson.log_level)
        self.assertEqual(d_client['num_nodes'], request.sheep['num_nodes'])

if __name__ == '__main__':
    unittest.main()
