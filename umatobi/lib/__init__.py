# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import json, time, os, threading, sched, configparser, re, shutil
import base64
from datetime import datetime as datetime2

import yaml
from umatobi.constants import *
from umatobi.log import *

def make_fixture(yaml_path, index):
    yaml_dir = os.path.dirname(yaml_path)
    schema_path, table_name, *components = load_yaml(yaml_path)[index]
    schema_path = os.path.join(yaml_dir, schema_path)
    schema_parser = SchemaParser(schema_path)
    fixture = tuple(schema_parser.parse_record(component, table_name) for component in components)
    return schema_parser, table_name, fixture

def inserts_fixture(db, yaml_path, index):
    schema_parser, table_name, fixture = make_fixture(yaml_path, index)
   #print('table_name =',table_name)
   #print('fixture =', fixture)
    if not table_name in db.get_table_names():
        db.create_table(table_name)
    listed_fixture = [tuple(fixture[0].keys())]
    listed_fixture.extend([tuple(x.values()) for x in fixture])
   #print('listed_fixture =', listed_fixture)

   #>>> L = [d.keys()]
   #>>> L
   #[dict_keys(['a', 'b', 'c'])]
   #>>> L.extend([x.values() for x in fix])
   #>>> L
   #[dict_keys(['a', 'b', 'c']), dict_values([1, 2, 3]), dict_values([4, 5, 6])]
    db.inserts(table_name, listed_fixture)
    db.commit()
    return schema_parser, table_name, fixture

def converter_blob(b64_encoded_string):
    return base64.b64decode(b64_encoded_string)

def converter_real(value):
    try:
        f = float(value)
    except ValueError as err:
        if err.args[0] == f"could not convert string to float: '{value}'":
            f = None
        else:
            raise err
    return f

def converter_integer(value):
    try:
        i = int(value)
    except ValueError as err:
        if err.args[0] == f"invalid literal for int() with base 10: '{value}'":
            i = None
        else:
            raise err
    return i

def converter_text(text):
    return str(text)

def converter_null(any_arg):
    return None

def validate_kwargs(st_barrier, kwargs):
    if st_barrier != kwargs.keys():
        st_unknown = kwargs.keys() - st_barrier
        st_must = st_barrier - kwargs.keys()
        message = ('unmatched st_barrier and kwargs.keys().\n'
                   'unknown keys are {},\n'
                   'must keys are {}').format(st_unknown, st_must)
        raise RuntimeError(message)

def bytes2dict(b):
    j = b.decode('utf-8')
    return json2dict(j)

def dict2bytes(d):
    j = dict2json(d)
    return j.encode('utf-8')

def dict2json(d):
    j = json.dumps(d)
    return j + '\n'

def json2dict(j):
    d = json.loads(j)
    return d

def tell_shutdown_time():
    shutdown_time = datetime_now()
    return shutdown_time

def load_yaml(yaml_path):
    with open(yaml_path) as f:
        y = yaml.load(f, Loader=yaml.SafeLoader)
    return y

def allot_numbers(total, an_allotment):
    # assign number equality
    if total <= an_allotment:
        heads = 1
        assigned_num = total
        last = total
    else:
        div, mod = divmod(total, an_allotment)
        if mod == 0:
            mod = an_allotment
        else:
            div += 1
        heads = div
        assigned_num = an_allotment
        last = mod

    return heads, assigned_num, last

def make_question_marks(n_questions):
    if not isinstance(n_questions, int):
        raise TypeError(f'make_question_marks(="{n_questions}") argument must be an integer.')
    if n_questions <= 0:
        raise ValueError(f'n_questions(={n_questions}) must be greater than or equal to one.')
    hatenas = '({})'.format(', '.join('?' * n_questions))
    return hatenas

def make_growing_dict(id_, et, pickle):

    growing = {
        'id': id_,
        'elapsed_time': et,
        'pickle': pickle,
    }

    return growing

class Polling(threading.Thread):

    @classmethod
    def sleep(cls, secs):
        logger.info(f'Polling.sleep(secs={secs})')
        time.sleep(secs)

    def __init__(self, polling_secs):
        threading.Thread.__init__(self)
        self.polling_secs = polling_secs
        self._sche = sched.scheduler(timefunc=time.time, delayfunc=Polling.sleep)
#       self._sche.enter(self.polling_secs, 1, self._polling, ()) # 犯人

    def polling(self):
        raise NotImplementedError()

    def is_continue(self):
        raise NotImplementedError()

    def _polling(self):
        if self.is_continue():
            self.polling()
            self._sche.enter(self.polling_secs, 1, self._polling, ())

    def run(self):
        self._sche.run()

class Records(object):
    pass

class SimulationTime(object):
    Y15S_FORMAT='%Y-%m-%dT%H%M%S'

    @classmethod
    def now(cls):
        return datetime2.now()

    @classmethod
    def iso8601_to_time(cls, iso8601format):
        start_up_orig = datetime2.fromisoformat(iso8601format)
        return SimulationTime(start_up_orig)

    @classmethod
    def time_to_iso8601(cls, simulation_time):
      # >>> datetime2.isoformat(now)
      # '2019-08-27T02:43:20.708976'
        return datetime2.isoformat(simulation_time.start_up_orig)

    @classmethod
    def y15s_to_time(cls, y15s):
        start_up_orig = \
            datetime2.strptime(y15s, SimulationTime.Y15S_FORMAT)
        return SimulationTime(start_up_orig)

    @classmethod
    def time_to_y15s(cls, simulation_time):
        start_up_orig = simulation_time.start_up_orig
        return start_up_orig.strftime(SimulationTime.Y15S_FORMAT)

    def __init__(self, start_up_orig=None):
        if not start_up_orig:
            self.start_up_orig = SimulationTime.now()
        else:
            self.start_up_orig = start_up_orig

    def __str__(self):
        return self.get_iso8601()

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.start_up_orig == other.start_up_orig

    def get_iso8601(self):
        return SimulationTime.time_to_iso8601(self)

    def get_y15s(self):
        return SimulationTime.time_to_y15s(self)

    def passed_seconds(self, now=None):
        if not now:
            now = SimulationTime.now()
        return (now - self.start_up_orig).total_seconds()

    def passed_ms(self, now=None):
        '''simulation 開始から現在までに経過したmilli秒数。'''

        if not now:
            now = SimulationTime.now()
        # relativeCreated の時間単位がmsのため、
        # elapsed_time()もms単位となるようにする。
        return int(self.passed_seconds(now) * 1000)

# def isoformat_to_start_up_orig(isoformat):
#   # >>> datetime2.fromisoformat('2019-08-27T02:43:20.708976')
#   # datetime2(2019, 8, 27, 2, 43, 20, 708976)
#     return datetime2.fromisoformat(isoformat)

# Y15S_FORMAT='%Y-%m-%dT%H%M%S'
# def y15sformat_time(t):
#     "'return time format '2012-11-02T232227'"
#     return t.strftime(Y15S_FORMAT)
#
# def current_y15sformat_time():
#     now = datetime_now()
#     return y15sformat_time(now)

# def y15sformat_parse(s):
#     return datetime2.strptime(s, Y15S_FORMAT)

class PathMaker(object):

    def __eq__(self, other):
        return self.simulation_time == other.simulation_time

    def __init__(self, simulation_time_or_start_up_orig=None):
        st_or_suo = simulation_time_or_start_up_orig
        if isinstance(st_or_suo, SimulationTime):
            self.simulation_time = st_or_suo
        else:
            self.simulation_time = SimulationTime(st_or_suo)

    def get_client_db_path(self, client_id):
        client_n_db = re.sub(ATAT_N, str(client_id), CLIENT_N_DB)
        return os.path.join(self.get_simulation_dir_path(), client_n_db)

    def get_simulation_dir_path(self):
        simulation_dir_path = re.sub(ATAT_SIMULATION_TIME,
                                     self.simulation_time.get_y15s(),
                                     UMATOBI_SIMULATION_DIR_PATH)
        return simulation_dir_path

    def get_simulation_db_path(self):
        simulation_db_path = os.path.join(self.get_simulation_dir_path(),
                                          SIMULATION_DB)
        return simulation_db_path

    def get_simulation_schema_path(self):
        simulation_schema_path = os.path.join(self.get_simulation_dir_path(),
                                              SIMULATION_SCHEMA)

        return simulation_schema_path

    def get_module_path(self):
        return UMATOBI_MODULE_PATH

    def set_simulation_schema(self):
        simulation_schema_path = self.get_simulation_schema_path()

        if not os.path.isfile(simulation_schema_path):
            self.make_simulation_dir()
            logger.info(f"shutil.copyfile(SIMULATION_SCHEMA_PATH={SIMULATION_SCHEMA_PATH}, simulation_schema_path={simulation_schema_path})")
            shutil.copyfile(SIMULATION_SCHEMA_PATH, simulation_schema_path)

        return simulation_schema_path

    def get_master_palm_txt_path(self):
        return os.path.join(self.get_simulation_dir_path(), MASTER_PALM_TXT)

    def make_simulation_dir(self, simulation_dir_path=None):
        if not simulation_dir_path:
            simulation_dir_path = self.get_simulation_dir_path()

        if not os.path.isdir(simulation_dir_path):
            logger.info(f"os.makedirs('{simulation_dir_path}')")
            os.makedirs(simulation_dir_path, exist_ok=True)

        return simulation_dir_path

class SchemaParser(configparser.ConfigParser):

    DATA_TYPE_CONVERTER = {
        'blob': converter_blob,
        'real': converter_real,
        'integer': converter_integer,
        'text': converter_text,
        'null': converter_null,
    }

    def __init__(self, schema_path):
        super().__init__()
        self.schema_path = schema_path
        with open(self.schema_path, encoding='utf-8') as schema:
            self.read_file(schema)

        self.table_names = self.sections
        self.converter_tables = {}

        self.construct_converter_tables()

    def construct_converter_tables(self):
        for table_name in self.table_names():
            self.converter_tables[table_name] = {}
            for column_name, as_string in self[table_name].items():
                data_type = as_string.split(' ')[0]
                self.set_converter(table_name, column_name, data_type)

    def get_table_names(self):
        return self.table_names()

    def get_columns(self, table_name):
        return self[table_name]

    def parse_record(self, record, table_name):
        d = {}
        for column_name, as_string in record.items():
            converter = self.get_converter(table_name, column_name)
            value = converter(as_string)
          # print('record =')
          # print(record)
          # print('table_name =')
          # print(table_name)
          # print('column_name =')
          # print(column_name)
          # print('converter =')
          # print(converter)
          # print('as_string =')
          # print(as_string)
          # print('value =')
          # print(value)
          # print()
            d[column_name] = value
        return d

    def spawn_records(self, config, table_names=tuple()):
        if not table_names:
            table_names = config.sections()

        records = Records()
        for table_name in table_names:
            record = self.parse_record(config[table_name], table_name)
            setattr(records, table_name, record)

        return records

    def set_converter(self, table_name, column_name, data_type):
        converter = self.DATA_TYPE_CONVERTER[data_type]
        self.converter_tables[table_name][column_name] = converter

    def get_converter(self, table_name, column_name):
        converter = self.converter_tables[table_name][column_name]
        return converter

if __name__ == '__main__':
    st = SimulationTime()
    print('st =', st)
    print('repr(st) =', repr(st))
  # st = 2019-10-20T13:09:26.307215
  # repr(st) = <__main__.SimulationTime object at 0x1083dd1d0>

    import umatobi
    print('umatobi.__path__ =', umatobi.__path__)
    import umatobi.lib
    print('umatobi.lib.__path__ =', umatobi.lib.__path__)
