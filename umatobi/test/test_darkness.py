import os
import sys
import threading, multiprocessing
import unittest
import queue

from umatobi.test import *
from umatobi.simulator.darkness import Darkness
from umatobi.lib import current_y15sformat_time

class DarknessTests(unittest.TestCase):
    def test_darkess_basic(self):
        simulation_dir = os.path.join(".", SIMULATION_DIR)

        darkness_id = 1
        client_id = 1
        start_up_time = current_y15sformat_time()
        dir_name = os.path.join(simulation_dir, start_up_time)
        log_level = 'INFO'
        nodes_per_darkness = 5
        first_node_id = 1
        num_darkness = 8
        # share with client and darknesses
        made_nodes = multiprocessing.Value('i', 0),
        # share with client and another darknesses
        leave_there =threading.Event()

        darkness_d_config = {
            'id':  darkness_id,
            'client_id':  client_id,
            'start_up_time':  start_up_time,
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
        self.assertFalse(darkness.bye_bye_nodes.is_set())
        self.assertEqual(darkness.client_db.db_path,
                         os.path.join(dir_name, f"client.{client_id}.db"))

if __name__ == '__main__':
    unittest.main()
