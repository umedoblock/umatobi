import sqlite3
import configparser
import os
import sys
import logging

from lib import LOGGER_FMT

class SQL(object):
    def __init__(self, owner=None, db_path=':memory:', schema_path=''):
        self.db_path = db_path
        self.schema_path = schema_path
        self._conn = None
        self._cur = None
        self._create_table = {}
        self.owner = owner
        logger = getattr(owner, 'logger', None)
        self.set_logger(logger)
        self._schema = None

        if self.schema_path:
            self._schema = configparser.ConfigParser()
            with open(self.schema_path) as f:
                self._schema.read_file(f)

    def set_logger(self, logger, level='INFO'):
        if logger is None:
            # #139 いつかどこかで暇な時にでも、lib.make_logger() と統合しよう。
            logger = logging.getLogger(str(self))
            logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter(LOGGER_FMT)
            # print() の代わりとして使用することを想定しているので、
            # log message を sys.stdout に出力。
            ch = logging.StreamHandler(stream=sys.stdout)
            ch.setLevel(level)
            ch.setFormatter(formatter)
            logger.addHandler(ch)

        self.logger = logger

    def access_db(self):
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
      # self.logger.debug('name =', table_info.name)
      # self.logger.debug('table_info =', table_info)

        columns = []
        for column_name, explain in table_info.items():
            # ignored comment part
            sp = explain.split('#')
            column = ' '.join([column_name, sp[0]])
            columns += [column]
        sql = 'create table {} ({})'.format(table_name, ', '.join(columns))
        self._create_table[table_name] = sql
        self.execute(sql)

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

        self._conn.executemany(static_part + hatenas, tups[1:])

    def insert(self, table_name, d):
        static_part = 'insert into {} {} values '.format(table_name, tuple(d.keys()))
        hatenas = '({})'.format(', '.join('?' * len(d)))
        values = tuple(d.values())

        sql = static_part + str(values)
        self.logger.debug('{}'.format(sql))
        self.execute(static_part + hatenas, values)
        return sql

    def update(self, table_name, d, where):
        static_part = 'update {} set '.format(table_name)
        self.logger.debug('tuple(d.keys()) =', tuple(d.keys()))
        set_part = ', '.join(['{} = ?'.format(column) for column in d.keys()])
        set_part += ' '
        s = ' and '.join(['{} = {}'.format(k, v) for k, v in where.items()])
        where_clause = 'where {}'.format(s)
        values = tuple(d.values())

        self.logger.debug('static_part =', static_part)
        self.logger.debug('set_part =', set_part)
        self.logger.debug('s =', s)
        self.logger.debug('where_clause =', where_clause)
        self.logger.debug('')
        sql = static_part + set_part + where_clause
        self.logger.debug('for update sql =')
        self.logger.debug(sql)
        self.execute(sql, values)
        return static_part + str(values)

  # def __getattr__(self, name):
  #     self.logger.info('called __getattr__() with name={}'.format(name))

    def select(self, table_name, select_columns='*', conditions=''):
        sql = 'select {} from {} {};'. \
               format(select_columns, table_name, conditions)
        self.logger.debug('{} select sql =\n{}'.format(self.owner, sql))
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
        message = 'SQL(owner={}, db_path="{}", schema_path="{}")'. \
                   format(self.owner, self.db_path, self.schema_path)
        return message
