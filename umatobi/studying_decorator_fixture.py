import yaml

from umatobi.simulator.sql import SQL
from umatobi.tests import *

# Factorial program with memoization using
# decorators.
# https://www.geeksforgeeks.org/memoization-using-decorators-in-python/

def debug(f1):
    print('before2')
    def inner(num):
        print('before')
        f1(num)
        print('after')
        return True
    print('after2')
    print('--')
    return inner

def load_yaml_test1(yaml_path, key):
    with open(yaml_path) as f:
        y = yaml.load(f, Loader=yaml.SafeLoader)
      # y = yaml.safe_load(f, Loader=yaml.SafeLoader)
    print('y =', y)

def fixture(yaml_path, key):
    with open(yaml_path) as f:
        y = yaml.load(f, Loader=yaml.SafeLoader)
      # y = yaml.safe_load(f, Loader=yaml.SafeLoader)
    print('y =', y)
  # def inner(db, table, key, value):
    def inner(db, table, key, value):
        row = db.select('* from table where key=value')
        return row

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
#   facto(5)
#   print()

#   print(func(6))

#   sample()

    load_yaml_test1(TEST_YAML_PATH + ".1", 'foo')
#   fixture(TEST_YAML_PATH, 'foo')
