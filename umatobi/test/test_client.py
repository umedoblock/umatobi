import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from simulator.client import Client

test_dir = os.path.dirname(__file__)

class Testclient(unittest.TestCase):
  # def test_client_basic(self):
  #     watson = ('localhost', 65530)
  #     num_nodes = 10
  #     simulation_dir = os.path.join(test_dir, 'umatobi-simulation')

  #     client = Client(watson, num_nodes, simulation_dir)

  #     start_up = get_start_up()

  #   # db_dir = os.path.join(simulation_dir, start_up)
  #   # client_log = os.path.join(db_dir, 'client.log')

  #   # # clientが書き出す log 用の directory 作成
  #   # os.makedirs(db_dir)

  #   # self.assertFalse(os.path.exists(client_log))

  #   # self.assertTrue(os.path.exists(client_log))

  #   # # avoid warning
  #   # client.client.close()

    def test_client_cannot_say_hello(self):
        watson = ('localhost', 65530)
        num_nodes = 10
        simulation_dir = os.path.join(test_dir, 'umatobi-simulation')

        with self.assertRaises(RuntimeError) as raiz:
            client = Client(watson, num_nodes, simulation_dir)

        args = raiz.exception.args
        message = ('client cannot say "hello" to watson who is '
                   '{}').format(watson)
        self.assertEqual(message, args[0])

if __name__ == '__main__':
    unittest.main()

