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
            column = ' '.join([column_name, explain])
            columns += [column]
        sql = 'create table {} ({})'.format(table_name, ', '.join(columns))
        self._create_table[table_name] = sql
        self.cur.execute(sql)

    def insert(self, table_name, d):
        hatenas = '({})'.format(', '.join('?' * len(d)))
        sql = 'insert into {} {} values {}'. \
               format(table_name, tuple(d.keys()), hatenas)
        values = tuple(d.values())
        print('insert sql =')
        print(sql)
        print('values =')
        print(values)
        self.cur.execute(sql, values)

    def select(self, table_name, select_columns='*', conditions=''):
        sql = 'select {} from {} {}'. \
               format(select_columns, table_name, conditions)
        print('select sql =')
        print(sql)
        self.cur.execute(sql)
        # rows[0] の先頭からの順番と、
        # schema で記述している column の順番は一致する
        rows = self.cur.fetchmany()
        return rows
