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
            self.cur.execute(sql, values)
        else:
            self.cur.execute(sql)

    def close(self):
        self.cur.close()
        self.conn.close()

    def insert(self, table_name, d):
        static_part = 'insert into {} {} values '.format(table_name, tuple(d.keys()))
        hatenas = '({})'.format(', '.join('?' * len(d)))
        values = tuple(d.values())

        sql = static_part + str(values)
        print('{}'.format(sql))
        self.execute(static_part + hatenas, values)
        self.commit()
        return sql

    def update(self, table_name, d, where):
        static_part = 'update {} set '.format(table_name)
        print('tuple(d.keys()) =', tuple(d.keys()))
        set_part = ', '.join(['{} = ?'.format(column) for column in d.keys()])
        set_part += ' '
        s = ' and '.join(['{} = {}'.format(k, v) for k, v in where.items()])
        where_clause = 'where {}'.format(s)
        values = tuple(d.values())

        print('static_part =', static_part)
        print('set_part =', set_part)
        print('s =', s)
        print('where_clause =', where_clause)
        print()
        sql = static_part + set_part + where_clause
        print('for update sql =')
        print(sql)
        self.execute(sql, values)
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
