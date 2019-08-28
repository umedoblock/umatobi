import os
import sys
import threading, multiprocessing
import unittest
import queue

from umatobi.tests import *
from umatobi.simulator.darkness import Darkness, ExhaleQueue
from umatobi.lib import make_start_up_orig, make_start_up_time
from umatobi.simulator import sql

class DarknessAsClient(threading.Thread):
    def __init__(self, darkness_tests, darkness):
        threading.Thread.__init__(self)
        self.darkness_tests = darkness_tests
        self.darkness = darkness

    def run(self):
        self.darkness.im_sleeping.wait()
        self.darkness_tests.assertFalse(self.darkness.byebye_nodes.is_set())
        self.darkness_tests.assertFalse(self.darkness.all_nodes_inactive.is_set())

        incremented_threads = 2 * self.darkness.num_nodes
        # increment incremented_threads num_nodes for node threads
        # increment incremented_threads num_nodes for open_office_node threads
        # Because each node has an open_office_node thread
        if self.darkness._exhale_queue.is_alive():
            # increment incremented_threads 1 for Polling if it is alive
            incremented_threads += 1
        self.darkness_tests.assertEqual(threading.active_count(),
                     1 + 1 + incremented_threads)
        # above why "1 + 1" ?
        #       left 1     means of cource main thread.
        #      right     1 means this DarknessAsClient thread.
        # Therefore   "+ 1" must be there. right ?
        self.darkness_tests.assertEqual(self.darkness.made_nodes.value,
                                        self.darkness.num_nodes)

        # Originally client set leave_there event.
        self.darkness.leave_there.set()
        # client become leave mode.

class DarknessTests(unittest.TestCase):
    def setUp(self):
        darkness_id = 1
        client_id = 1
        start_up_orig = make_start_up_orig()
        dir_name = os.path.join(SIMULATION_DIR, make_start_up_time(start_up_orig))
        log_level = 'INFO'
        nodes_per_darkness = Darkness.NODES_PER_DARKNESS
        first_node_id = 1
        num_darkness = 8
        # share with client and darknesses
        made_nodes = multiprocessing.Value('i', 0)
        # share with client and another darknesses
        leave_there =threading.Event()

        self.darkness_d_config = {
            'id':  darkness_id,
            'client_id':  client_id,
            'start_up_orig':  start_up_orig,
            'dir_name':  dir_name,
            'log_level':  log_level,
            'num_nodes':  nodes_per_darkness,
            'first_node_id':  first_node_id,
            'num_darkness': num_darkness,
            # share with client and darknesses
            'made_nodes':  made_nodes,
            # share with client and another darknesses
            'leave_there':  leave_there,
        }

        self.darkness = Darkness(**self.darkness_d_config)

        for k, v in self.darkness_d_config.items():
            attr = getattr(self.darkness, k)
            self.assertEqual(v, attr)

    def tearDown(self):
        self.darkness.byebye_nodes.set()

    def test_darkess___init__(self):
        darkness_d_config = self.darkness_d_config
        darkness = self.darkness

        leave_there = darkness_d_config['leave_there']
        dir_name = darkness_d_config['dir_name']
        client_id = darkness_d_config['client_id']

        self.assertEqual(darkness.leave_there, leave_there)
        self.assertFalse(darkness.leave_there.is_set())

        self.assertEqual(darkness.client_db.db_path,
                         os.path.join(dir_name, f"client.{client_id}.db"))
        self.assertEqual(darkness.schema_path, SCHEMA_PATH)
        self.assertIsInstance(darkness.client_db, sql.SQL)

        self.assertEqual(darkness._queue_darkness.qsize(), 0)
        self.assertFalse(darkness.all_nodes_inactive.is_set())
        self.assertFalse(darkness.im_sleeping.is_set())
        self.assertIsInstance(darkness._exhale_queue, ExhaleQueue)
        self.assertFalse(darkness.byebye_nodes.is_set())

        self.assertEqual(darkness.nodes, [])

    def test_darkess_start(self):
        darkness_d_config = self.darkness_d_config
        darkness = self.darkness

        leave_there = darkness_d_config['leave_there']
        dir_name = darkness_d_config['dir_name']
        client_id = darkness_d_config['client_id']

        self.assertFalse(darkness.byebye_nodes.is_set())
        self.assertEqual(darkness.leave_there, leave_there)
        self.assertEqual(darkness.client_db.db_path,
                         os.path.join(dir_name, f"client.{client_id}.db"))
        self.assertListEqual(darkness.nodes, [])
        self.assertEqual(darkness._queue_darkness.qsize(), 0)
        self.assertFalse(darkness.all_nodes_inactive.is_set())
        self.assertFalse(darkness.im_sleeping.is_set())

        client_db = sql.SQL(db_path=darkness.client_db_path,
                            schema_path=SCHEMA_PATH)
        client_db.create_db()
        client_db.create_table('growings')
        client_db.close()

        self.assertEqual(threading.active_count(), 1)
        # "1" means of course a main thread.
        self.assertFalse(darkness.byebye_nodes.is_set())

        ######################################################################
        # Originally client set darkness.leave_there event. ##################
        # But there is no client. Therefore darkness must play client role. ##
        ######################################################################
        darkness_as_client = DarknessAsClient(self, darkness)
        darkness_as_client.start()

        darkness.start()

        self.assertTrue(darkness.all_nodes_inactive.is_set())
        self.assertTrue(darkness.byebye_nodes.is_set())
        self.assertEqual(threading.active_count(), 1)

    def test_darkness__spawn_nodes(self):
        darkness = self.darkness

        for node in darkness.nodes:
            self.assertFalse(node.im_ready.is_set())
        self.assertEqual(len(darkness.nodes), 0)
        darkness._spawn_nodes()
        self.assertEqual(len(darkness.nodes), darkness.num_nodes)
        self.assertEqual(darkness.made_nodes.value, darkness.num_nodes)
        for node in darkness.nodes:
            self.assertTrue(node.im_ready.is_set())

    def test_darkness__sleeping(self):
        darkness = self.darkness
        darkness.num_nodes = 0
        self.assertFalse(darkness.leave_there.is_set())
        self.assertFalse(darkness.im_sleeping.is_set())

        darkness_as_client = DarknessAsClient(self, darkness)

        darkness_as_client.start() # darkness.leave_there.set()
        darkness._sleeping()       # darkness.im_sleeping.set()
        self.assertTrue(darkness.leave_there.is_set())
        self.assertTrue(darkness.im_sleeping.is_set())

    def test_darkness__leave_here(self):
        darkness = self.darkness
        darkness._exhale_queue.start() # for ExhaleQueue object
        darkness._spawn_nodes()

        client_db = sql.SQL(db_path=darkness.client_db_path,
                            schema_path=SCHEMA_PATH)
        client_db.create_db()
        client_db.create_table('growings')
        client_db.close()

        self.assertFalse(darkness.byebye_nodes.is_set())
        self.assertFalse(darkness.all_nodes_inactive.is_set())
        self.assertEqual(len(darkness.nodes), darkness.num_nodes)
        for node in darkness.nodes:
            self.assertTrue(node.is_alive())
        self.assertTrue(darkness._exhale_queue.is_alive())

        darkness._leave_here()

        self.assertTrue(darkness.byebye_nodes.is_set())
        self.assertTrue(darkness.all_nodes_inactive.is_set())
        self.assertEqual(len(darkness.nodes), darkness.num_nodes)
        for node in darkness.nodes:
            self.assertFalse(node.is_alive())
        self.assertFalse(darkness._exhale_queue.is_alive())

    def test_darkness__stop(self):
        darkness = self.darkness
        darkness._spawn_nodes()

        self.assertEqual(len(darkness.nodes), darkness.num_nodes)
        with self.assertLogs('umatobi', level='INFO') as cm:
            darkness._stop()
        self.assertEqual(len(cm.output), darkness.num_nodes)
        self.assertRegex(cm.output[0], r'^INFO:umatobi:Darkness\(id=\d+\)._stop\(\) Node\(id=\d+, addr=\(\'localhost\', 10001\)\)')

if __name__ == '__main__':
    unittest.main()
