import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from simulator.client import Client

test_dir = os.path.dirname(__file__)

class Testclient(unittest.TestCase):
    def test_client_cannot_say_hello(self):
        watson = ('localhost', 65530)
        num_nodes = 10
        simulation_dir = os.path.join(test_dir, 'umatobi-simulation')

        with self.assertRaises(RuntimeError) as raiz:
            client = Client(watson, num_nodes, simulation_dir)

        args = raiz.exception.args
        message = ('client cannot say "I am Client." to watson who is '
                   '{}').format(watson)
        self.assertEqual(message, args[0])

if __name__ == '__main__':
    unittest.main()

