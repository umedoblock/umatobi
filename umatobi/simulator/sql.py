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
