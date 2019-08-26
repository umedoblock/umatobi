import os
import sys
import threading, multiprocessing
import unittest
import queue

from umatobi.tests import *
from umatobi.simulator.darkness import Darkness
from umatobi.lib import make_start_up_orig, make_start_up_time
from umatobi.simulator import sql

class DarknessTests(unittest.TestCase):
    def test_darkess_basic(self):
        simulation_dir = os.path.join(".", SIMULATION_DIR)

        darkness_id = 1
        client_id = 1
        start_up_orig = make_start_up_orig()
        dir_name = os.path.join(simulation_dir, make_start_up_time(start_up_orig))
        log_level = 'INFO'
        nodes_per_darkness = 5
        first_node_id = 1
        num_darkness = 8
        # share with client and darknesses
        made_nodes = multiprocessing.Value('i', 0)
        print("made_nodes =", made_nodes)
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
        self.assertEqual(darkness.client_db.db_path,
                         os.path.join(dir_name, f"client.{client_id}.db"))

        client_db = sql.SQL(db_path=darkness.client_db_path,
                            schema_path=SCHEMA_PATH)
        client_db.create_db()
        client_db.create_table('growings')
        darkness.leave_there.set() # for test
        self.assertFalse(darkness.byebye_nodes.is_set())
        darkness.start()
        self.assertTrue(darkness.all_nodes_inactive.is_set())

        self.assertTrue(darkness.byebye_nodes.is_set())
        darkness.leave_there.set()
        self.assertTrue(darkness.byebye_nodes.is_set())
        self.assertTrue(darkness.all_nodes_inactive.is_set())

        darkness.stop()

if __name__ == '__main__':
    unittest.main()
