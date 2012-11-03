import sqlite3
import configparser

class SQL(object):
    def __init__(self, db_path=':memory:', schema_path=None):
        if schema_path is None:
            RuntimeError('schema_path must be available path.')
        self.db_path = db_path
        self.schema_path = schema_path
        self.conn = None
        self.cur = None
        self._create_table = {}

        self.schema = configparser.ConfigParser()
        with open(self.schema_path) as f:
            self.schema.read_file(f)

    def create_db(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cur = self.conn.cursor()

    def create_table(self, table_name):
        if self.conn is None:
            raise RuntimeError('you must call read_table_schema() before call create_table().')

        table_info = self.schema[table_name]
      # print('name =', table_info.name)
      # print('table_info =', table_info)

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
        self.conn.commit()

    def execute(self, sql, values=()):
        if values:
            self.cur.execute(sql, values)
        else:
            self.cur.execute(sql)

    def insert(self, table_name, d):
        static_part = 'insert into {} {} values '.format(table_name, tuple(d.keys()))
        hatenas = '({})'.format(', '.join('?' * len(d)))
        values = tuple(d.values())

        self.execute(static_part + hatenas, values)
        self.commit()
        return static_part + str(values)

    def select(self, table_name, select_columns='*', conditions=''):
        sql = 'select {} from {} {}'. \
               format(select_columns, table_name, conditions)
        print('select sql =')
        print(sql)
        self.execute(sql)
        # rows[0] の先頭からの順番と、
        # schema で記述している column の順番は一致する
        rows = self.cur.fetchmany()
        return rows
