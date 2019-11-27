# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import yaml, datetime

from umatobi.simulator.sql import SQL
from umatobi.tests import *

# Factorial program with memoization using
# decorators.
# https://www.geeksforgeeks.org/memoization-using-decorators-in-python/

def debug(f1):
    print('before2')
    def inner(num):
        print('before')
        print('f1 =', f1)
        print('inner =', inner)
        print('num =', num)
        debug_got_by_f1 = f1(num)
        print('debug_got_by_f1 is', debug_got_by_f1)
        print('after')
        return debug_got_by_f1
    print('after2')
    print('--')
    return inner

def dump_yaml_test1():
    d = {
        'id': 1,
        'val_null':    None,
        'val_integer': 100,
        'val_real':    1.1,
        'val_text':    'text context',
        'val_blob':    b'binary strings',
        'now':         datetime.datetime(2011, 11, 11, 11, 11, 44, 901234),
    }

    dumped_yaml = yaml.dump(d)
    print('d =')
    print(d)
    print()
    print('dumped_yaml =')
    print(dumped_yaml)

def load_yaml_test1(yaml_path, key):
    with open(yaml_path) as f:
        y = yaml.load(f, Loader=yaml.SafeLoader)
      # y = yaml.safe_load(f, Loader=yaml.SafeLoader)
    print('y1 =', y)

# see in detail
# https://pyyaml.org/wiki/PyYAMLDocumentation

# import base64
# >>> base64.b64encode(b'binary')
# b'YmluYXJ5'
# >>> base64.b64decode(b'YmluYXJ5')
# b'binary'
# val_blob: !!binary |
#   YmluYXJ5
# val_blob: !!binary |
#   YmluYXJ5IHN0cmluZ3M=

def fixture(yaml_path, key):
    with open(yaml_path) as f:
        y = yaml.load(f, Loader=yaml.SafeLoader)
      # y = yaml.safe_load(f, Loader=yaml.SafeLoader)
    print('y =', y)
  # def inner(db, table, key, value):
    def inner(db, table, key, value):
        row = db.select('* from table where key=value')
        return row

# @fixture(TEST_ATAT_N_YAML_PATH + ".1", 'foo')
# def test_fixture_yaml_path1(fixture_load1):
#     with open(yaml_path) as f:
#         y = yaml.load(f, Loader=yaml.SafeLoader)
#       # y = yaml.safe_load(f, Loader=yaml.SafeLoader)
#     print('y =', y)
#
#   # def inner(db, table, key, value):
#     def inner(db, table, key, value):
#         row = db.select('* from table where key=value')
#         return row

@debug
def facto(num):
    print(f'facto({num})')
    if num == 1:
        return 1
    else:
        return num * facto(num-1)

@debug
def func(num):
    print(f'func(num={num})')

# @fixture('test.yaml', 'foo')
# def sample():
#     sql = SQL(db_path='fixture.db', schema_path=TEST_SCHEMA_PATH)
#     sql.create_db()
#     sql.create_table('test_table')
# 
#     sql.remove_db()

if __name__ == '__main__':
    v = facto(5)
    print('fact(5) return v =', v)
#   print()

#   print(func(6))

#   sample()

    dump_yaml_test1()
    load_yaml_test1(TEST_ATAT_N_YAML_PATH.replace(ATAT_N, '1'), 'foo')
#   fixture(TEST_ATAT_N_YAML_PATH, 'foo')
