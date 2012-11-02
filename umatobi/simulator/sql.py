import sqlite3

class SQL(object):
    def __init__(self, db_path=':memory:', schema_path=None):
        if schema_path is None:
            RuntimeError('schema_path must be available path.')
        self.db_path = db_path
        self.schema_path = schema_path
        self.conn = None
        self.cur = None

        schema = configparser.ConfigParser()
        with open(self.schema_path) as f:
            schema.read_file(f, table_name)

    def create_db(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cur = self.conn.cursor()

    def create_table(self, table_name):
        if self.conn is None:
            raise RuntimeError('you must call read_table_schema() before call create_table().')
        print(self.schema)
      # if not table_name in self.schema:
