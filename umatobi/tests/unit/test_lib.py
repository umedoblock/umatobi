# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import os, pathlib, pickle
import unittest
from datetime import datetime, timedelta

import yaml
from umatobi.tests import *
from umatobi.tests.constants import *
from umatobi.lib import *
from umatobi.simulator.node import Node

class LibTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.simulation_time = SimulationTime()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.simulation_time = LibTests.simulation_time

    def tearDown(self):
        pass

    def test_validate_kwargs(self):
        pass

    def test_dict2bytes(self):
        d = {
            'port': 1000,
            'host': 'localhost',
            'key': '0x' + '1234567890abcedf' * 4,
        }

        self.assertIsInstance(d, dict)
        b = dict2bytes(d)
        self.assertIsInstance(b, bytes)
        self.assertEqual(b, b'{"port": 1000, "host": "localhost", "key": "0x1234567890abcedf1234567890abcedf1234567890abcedf1234567890abcedf"}\n')

    def test_bytes2dict(self):
        d = {
            'port': 1000,
            'host': 'localhost',
            'key': '0x' + '1234567890abcedf' * 4,
        }
        expected_d = d

        b = dict2bytes(d)
        d2 = bytes2dict(b)
        self.assertIsInstance(d2, dict)
        self.assertNotEqual(id(d2), id(d))
        self.assertEqual(d2, expected_d)

    def test_dict2json(self):
        d = {
            'port': 1000,
            'host': 'localhost',
            'key': '0x' + '1234567890abcedf' * 4,
        }

        self.assertIsInstance(d, dict)
        j = dict2json(d)
        self.assertIsInstance(j, str)
        self.assertEqual(j, '{"port": 1000, "host": "localhost", "key": "0x1234567890abcedf1234567890abcedf1234567890abcedf1234567890abcedf"}\n')

    def test_json2dict(self):
        d = {
            'port': 1000,
            'host': 'localhost',
            'key': '0x' + '1234567890abcedf' * 4,
        }
        expected_d = d

        j = dict2json(d)
        d2 = json2dict(j)
        self.assertIsInstance(d2, dict)
        self.assertNotEqual(id(d2), id(d))
        self.assertEqual(d2, expected_d)

    def test_tell_shutdown_time(self):
        pass

    def test_load_yaml(self):
        y = load_yaml(replace_atat_n('1'))
        expected_obj = {'a': 1}
        self.assertEqual(y, expected_obj)

    def test_load_yaml2(self):
        y = load_yaml(replace_atat_n('2'))
        expected_obj = {'b': {'c': 3, 'd': 4}}
        self.assertEqual(y, expected_obj)

    def test_load_yaml3(self):
        y = load_yaml(replace_atat_n('3'))
        expected_obj = {
            'e': {
                'id': 1,
                'now': datetime(2011, 11, 11, 11, 11, 44, 901234),
                'val_blob': b'binary',
                'val_integer': 100,
                'val_null': None,
                'val_real': 1.1,
                'val_text': 'text context'
            }
        }

        self.assertEqual(y, expected_obj)

    def test_load_yaml4(self):
        y = load_yaml(replace_atat_n('4'))
        expected_obj = {
            'foo': [
                'schema_path',
                 'table_name', {
                    'id': 1,
                    'val_blob': b'binary strings',
                    'val_num': 8,
                    'val_null': None
                }
            ]
        }

        self.assertEqual(y, expected_obj)

    def test_dump_yaml(self):
        d = {
            'id': 1,
            'val_null':    None,
            'val_integer': 100,
            'val_real':    1.1,
            'val_text':    'text context',
            'val_blob':    b'binary strings',
            'val_11':      b'\x11' * 32,
            'val_aa':      b'\xaa' * 32,
            'val_cc':      b'\xcc' * 32,
            'now':         datetime(2011, 11, 11, 11, 11, 44, 901234),
        }

        dumped_yaml = yaml.dump(d)
        expected_dump = '''id: 1
now: 2011-11-11 11:11:44.901234
val_11: !!binary |
  ERERERERERERERERERERERERERERERERERERERERERE=
val_aa: !!binary |
  qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqo=
val_blob: !!binary |
  YmluYXJ5IHN0cmluZ3M=
val_cc: !!binary |
  zMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMw=
val_integer: 100
val_null: null
val_real: 1.1
val_text: text context
'''
        self.assertEqual(dumped_yaml, expected_dump)

    def test_allot_numbers(self):
        total = 100
        an_allotment = 7
        # 14 = 100 // 7
        #  2 = 100  % 7
        heads, assigned_num, last = allot_numbers(total, an_allotment)
        self.assertEqual(heads, 15)
        self.assertEqual(assigned_num, 7)
        self.assertEqual(last, 2)

        total = 100
        an_allotment = 10
        heads, assigned_num, last = allot_numbers(total, an_allotment)
        self.assertEqual(heads, 10)
        self.assertEqual(assigned_num, 10)
        self.assertEqual(last, 10)

        total = 99
        an_allotment = 100
        heads, assigned_num, last = allot_numbers(total, an_allotment)
        self.assertEqual(heads, 1)
        self.assertEqual(assigned_num, total)
        self.assertEqual(last, total)

        total = 100
        an_allotment = 100
        heads, assigned_num, last = allot_numbers(total, an_allotment)
        self.assertEqual(heads, 1)
        self.assertEqual(assigned_num, total)
        self.assertEqual(last, total)

        total = 101
        an_allotment = 100
        heads, assigned_num, last = allot_numbers(total, an_allotment)
        self.assertEqual(heads, 2)
        self.assertEqual(assigned_num, an_allotment)
        self.assertEqual(last, 1)

    def test_make_growing_dict(self):
        from datetime import timedelta

        node_assets = make_node_assets()

        node = Node(host='localhost', id=1, **node_assets)
        key = b'\x01\x23\x45\x67\x89\xab\xcd\xef' * 4
        node.key.update(key)
        got_attrs = node.get_attrs()
        pickled_attrs = pickle.dumps(got_attrs)
        expected_growing_dict = {
            'id': 100,
            'elapsed_time': 111,
            'pickle': pickled_attrs,
        }

        simulation_time = SimulationTime()
        with time_machine(simulation_time.start_up_orig + \
                          timedelta(milliseconds=111)):
            elapsed_time = simulation_time.passed_ms()

        growing_dict = make_growing_dict(100, elapsed_time, pickled_attrs)

        self.assertEqual(growing_dict, expected_growing_dict)

if __name__ == '__main__':
    unittest.main()
