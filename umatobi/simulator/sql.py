import sqlite3, configparser, os, sys, logging

from umatobi.log import *

# print("__name__ =", __name__)
# __name__ = simulator.sql
# print("__file__ =", __file__)
# __file__ = umatobi/tools/../simulator/sql.py

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
        logger.info(f"SQL(db_path={db_path}, schema_path={schema_path})")
        self.db_path = db_path
        self.schema_path = schema_path
        self._conn = None
        self._cur = None
        self._create_table = {}
        self._schema = None
        self._closed = True

        if self.schema_path and os.path.isfile(self.schema_path):
            self.read_schema()

    def read_schema(self):
        logger.info(f"{self}.read_schema(), schema_path={self.schema_path}")
        self._schema = configparser.ConfigParser()
        with open(self.schema_path, encoding='utf-8') as f:
            self._schema.read_file(f)

    def access_db(self):
        logger.info(f"{self}.access_db(), db_path={self.db_path}")
        if not os.path.exists(self.db_path):
            raise RuntimeError(f"cannot find db_path='{self.db_path}'")
        self.create_db()

    def create_db(self):
        logger.info(f"{self}.create_db(), db_path={self.db_path}")
        if self.db_path != ":memory:":
            db_dir_name = os.path.dirname(self.db_path)
            if db_dir_name and not os.path.isdir(db_dir_name):
                logger.debug(f"{self}, not os.path.isdir({db_dir_name})")
                os.makedirs(db_dir_name, exist_ok=True)
        try:
            self._conn = sqlite3.connect(self.db_path)
            self._closed = False
        except sqlite3.OperationalError as e:
            if e.args[0] != 'unable to open database file':
                raise(e)
            db_dir_name = os.path.dirname(self.db_path)
            dir_exists = os.path.exists(db_dir_name)
            db_exists = os.path.exists(self.db_path)
            raise ValueError(f"{self}.create_db() cannot open db_path={self.db_path}, db_exists={db_exists}, db_dir_name={db_dir_name}, dir_exists={dir_exists}")
        self._conn.row_factory = sqlite3.Row
        self._cur = self._conn.cursor()

    def remove_db(self):
        logger.debug(f"{self}.remove_db(), db_path={self.db_path}")
        if self.db_path != ":memory:":
            if os.path.isfile(self.db_path):
                logger.info(f"{self} os.remove(db_path={self.db_path})")
                os.remove(self.db_path)
            else:
                logger.info(f"{self} not found db_path={self.db_path}.")

    def create_table(self, table_name):
        logger.info(f"{self}.create_table(table_name={table_name})")
        # ここまで頑張ったところで力尽きました。
        # もう，logger を入れるのは辞めます。
        if self._conn is None:
            raise RuntimeError('you must call read_table_schema() before call create_table().')

        table_info = self._schema[table_name]

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
            logger.info(f"{self}._cur(={self._cur}).execute(sql={sql}, values={values})")
            rows = self._cur.execute(sql, values)
        else:
            rows = self._cur.execute(sql)
            logger.debug(f"{self}._cur(={self._cur}).execute(sql={sql})")
        return rows

    def close(self):
        self.commit()
        self._cur.close()
        self._conn.close()
        self._closed = True

    def closed(self):
        return self._closed

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
        self.select(table_name, conditions='limit 1')
        column_names = tuple(map(lambda x: x[0], self._cur.description))
        return column_names

    def get_dict_of_columns(self, table_name):
        column_names = self.get_column_names(table_name)
      # print('column_names =', column_names)
        d = {}
        for i, column_name in enumerate(column_names):
            d[column_name] = i
        return d

    def __str__(self):
        message = 'SQL(db_path="{}", schema_path="{}")'. \
                   format(self.db_path, self.schema_path)
        return message
