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

def fixture(schema, table_name, key=None):
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

def sample():
    sql = SQL(db_path=TEST_DB_PATH, schema_path=TEST_SCHEMA_PATH)
    sql.create_db()
    sql.create_table('test_table')

    sql.remove_db()

if __name__ == '__main__':
    facto(5)
    print()

    print(func(6))

    sample()
