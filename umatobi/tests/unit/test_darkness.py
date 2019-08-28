import os
import sys
import threading, multiprocessing
import unittest
import queue

from umatobi.tests import *
from umatobi.simulator.darkness import Darkness
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

        incremented_threads = 1 + 2 * self.darkness.num_nodes
        # increment incremented_threads 1 for Polling
        # increment incremented_threads num_nodes for node threads
        # increment incremented_threads num_nodes for open_office_node threads
        # Because each node has an open_office_node thread
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
    def test_darkess_basic(self):
        darkness_id = 1
        client_id = 1
        start_up_orig = make_start_up_orig()
        dir_name = os.path.join(SIMULATION_DIR, make_start_up_time(start_up_orig))
        log_level = 'INFO'
        nodes_per_darkness = 5
        first_node_id = 1
        num_darkness = 8
        # share with client and darknesses
        made_nodes = multiprocessing.Value('i', 0)
        # share with client and another darknesses
        leave_there =threading.Event()

        darkness_d_config = {
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

        darkness = Darkness(**darkness_d_config)
        for k, v in darkness_d_config.items():
            attr = getattr(darkness, k)
            self.assertEqual(v, attr)
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

if __name__ == '__main__':
    unittest.main()
