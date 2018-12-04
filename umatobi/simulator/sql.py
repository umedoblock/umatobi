import sqlite3
import configparser
import os
import sys
import logging

from lib import LOGGER_FMT, make_logger
from lib.args import get_logger_args

# print("__name__ =", __name__)
# __name__ = simulator.sql
# print("__file__ =", __file__)
# __file__ = umatobi/tools/../simulator/sql.py

global logger
logger_args = get_logger_args()
logger = make_logger(logger_args.simulation_dir, \
                     name=os.path.basename(__name__), \
                     level=logger_args.log_level)

class SQL(object):
    @staticmethod
    def construct_insert_by_dict(table_name, d):
        sql = ""
        _key_names = ("', '".join(['{}'] * len(d))).format(*d.keys())
        part_keys = f"('{_key_names}')"

        hatenas = '({})'.format(', '.join('?' * len(d)))
        sql = "insert into " + table_name + part_keys + " values" + hatenas
        values = tuple(d.values())
        return sql, values

    def __init__(self, db_path=':memory:', schema_path=''):
        self.db_path = db_path
        self.schema_path = schema_path
        self._conn = None
        self._cur = None
        self._create_table = {}
        self._schema = None

        if self.schema_path:
            self.read_schema()

    def read_schema(self):
        self._schema = configparser.ConfigParser()
        with open(self.schema_path) as f:
            self._schema.read_file(f)

    def access_db(self):
        logger.debug(f"self.db_path={self.db_path} in access_db()")
        if not os.path.exists(self.db_path):
            raise RuntimeError('cannot find "{}"'.format(self.db_path))
        self.create_db()

    def create_db(self):
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._cur = self._conn.cursor()

    def create_table(self, table_name):
        if self._conn is None:
            raise RuntimeError('you must call read_table_schema() before call create_table().')

        table_info = self._schema[table_name]
      # logger.debug('name =', table_info.name)
      # logger.debug('table_info =', table_info)

        columns = []
        for column_name, explain in table_info.items():
            # ignored comment part
            sp = explain.split('#')
            column = ' '.join([column_name, sp[0]])
            columns += [column]
        sql = 'create table {} ({})'.format(table_name, ', '.join(columns))
        self._create_table[table_name] = sql
        self.execute(sql)

    def select_one(self, table_name, column_name):
        record = self.select(table_name, select_columns=column_name,
                             conditions='limit 1')[0]
        return record[column_name]

    def drop_table(self, table_name):
        sql = 'drop table {}'.format(table_name)
        self.execute(sql)

    def init_table(self, table_name):
        try:
            self.drop_table(table_name)
        except sqlite3.OperationalError as raiz:
            if raiz.args[0] != 'no such table: {}'.format(table_name):
                raise raiz
        self.create_table(table_name)

    def take_table(self, src, table_name, auto_commit=True):
#       print('take_table() =================================================')
        self.init_table(table_name)

        records = src.select(table_name)
        L = []
#       print('records =', records)
        if self._conn.row_factory == sqlite3.Row:
#           print('records[0] =', records[0])
#           print('records[0].keys() =', records[0].keys())
#           print('tuple(records[0]) =', tuple(records[0]))
#           print()
            L.append(tuple(records[0].keys())) # column name
            for record in records:
                L.append(tuple(record))
        else:
            message = 'row_factory(={}) is unknown. Therefore fail safe occured.'.format(self._conn.row_factory)
            raise RuntimeError(message)
        tups = tuple(L)
#       print('tups =')
#       print(tups)
#       print()
        self.inserts(table_name, tups)
        if auto_commit:
            self.commit()

    def take_db(self, src):
        for table_name in src.get_table_names():
            self.take_table(src, table_name, auto_commit=False)
        self.commit()

    def commit(self):
        self._conn.commit()

    def execute(self, sql, values=()):
        # valuesが一つの場合、以下のようなsqlが発行されてしまう。
        # ('table_name',) (b'abc',)
        # 結果、例外が発生する。
        # sqlite3.OperationalError: near ")": syntax error
        sql = sql.replace("',)", "')")
        # replace() を実行してやると、綺麗になる。
        # ('table_name') (b'abc')
        # でも、雰囲気として、 replace() は必要ない。
        # だって、どのtableにも'id'があるんだもん。。。
        # valuesの要素が一つだなんて事はなさそうだよ。
        # でも、せっかく書いた replace()。
        # 消すのはもったいないので残す。
        if values:
            rows = self._cur.execute(sql, values)
        else:
            rows = self._cur.execute(sql)
        return rows

    def close(self):
        self._cur.close()
        self._conn.close()

    def inserts(self, table_name, tups):
      # print('tups =', tups)
        columns = tups[0]
        static_part = 'insert into {} {} values '.format(table_name, columns)
        hatenas = '({})'.format(', '.join('?' * len(columns)))

        logger.debug('static_part + hatenas =')
        logger.debug(static_part + hatenas)
        logger.debug("values=")
        logger.debug(tups[1:])
        self._conn.executemany(static_part + hatenas, tups[1:])

    def insert(self, table_name, d):
        sql, values = SQL.construct_insert_by_dict(table_name, d)

        logger.debug(f'sql={sql} in SQL.insert()')
        logger.debug(f'values={values} in SQL.insert()')
        self.execute(sql, values)
        return sql, values

    def update(self, table_name, d, where):
        static_part = 'update {} set '.format(table_name)
        logger.debug(f'tuple(d.keys()) = {tuple(d.keys())}')
        set_part = ', '.join(['{} = ?'.format(column) for column in d.keys()])
        set_part += ' '
        s = ' and '.join(['{} = {}'.format(k, v) for k, v in where.items()])
        where_clause = 'where {}'.format(s)
        values = tuple(d.values())

        logger.debug(f'static_part = {static_part}')
        logger.debug(f'set_part ={set_part}')
        logger.debug(f's = {s}')
        logger.debug(f'where_clause = {where_clause}')
        sql = static_part + set_part + where_clause
        logger.debug('update sql=')
        logger.debug(sql)
        logger.debug('values=')
        logger.debug(values)
        self.execute(sql, values)
        return static_part + str(values)

  # def __getattr__(self, name):
  #     logger.info('called __getattr__() with name={}'.format(name))

    def select(self, table_name, select_columns='*', conditions=''):
        sql = 'select {} from {}'. \
               format(select_columns, table_name)
        if conditions:
            sql += f" {conditions}"
        sql += ';'
        logger.debug(f'select sql=')
        logger.debug(sql)
        self.execute(sql)
        # rows[0] の先頭からの順番と、
        # schema で記述している column の順番は一致する
        rows = self._cur.fetchall()
        return rows

    def get_table_names(self):
        sql = 'select * from sqlite_master;'
        rows = self.execute(sql)
      # print(self.get_column_names())
      # ('type', 'name', 'tbl_name', 'rootpage', 'sql')
        tables = []
        for row in rows:
            if row[0] == 'table' and row[2] != 'sqlite_sequence':
                tables.append(row[2])
        logger.debug('tuple(tables)=')
        logger.debug(tuple(tables))

        return tuple(tables)

    def get_table_schema(self, table_name):
        sql = 'select * from sqlite_master;'
        rows = self.execute(sql)
      # print(self.get_column_names())
      # ('type', 'name', 'tbl_name', 'rootpage', 'sql')
        tables = []
        for row in rows:
            if table_name == row[2]:
                schema = row[4]
                break
        else:
            schema = 'cannot find "{}" table.'.format(table_name)
        return schema

    def get_column_names(self, table_name):
        '''return column names'''
        # http://www.python.org/dev/peps/pep-0249/
        # Cursor attributes
        #
        # .description
        #
        #     This read-only attribute is a sequence of 7-item sequences.
        #
        #     Each of these sequences contains information describing one
        #     result column:
        #
        #         name
        #         type_code
        #         display_size
        #         internal_size
        #         precision
        #         scale
        #         null_ok
        #
        #     The first two items (name and type_code) are mandatory, the other
        #     five are optional and are set to None if no meaningful values can
        #     be provided.
        #
        #     This attribute will be None for operations that do not return
        #     rows or if the cursor has not had an operation invoked via the
        #     .execute*() method yet.
        #
        #     The type_code can be interpreted by comparing it to the Type
        #     Objects specified in the section below.
        self.select(table_name, conditions='limit 1')
        column_names = tuple(map(lambda x: x[0], self._cur.description))
        return column_names

    def __str__(self):
        message = 'SQL(db_path="{}", schema_path="{}")'. \
                   format(self.db_path, self.schema_path)
        return message
