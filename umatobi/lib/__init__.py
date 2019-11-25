# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import json, time, os, threading, sched, configparser, socket, re, shutil
import base64
from datetime import datetime as datetime2

import yaml
from umatobi.constants import *
from umatobi.log import *

ADDRESS_FAMILY = {
    'v4': socket.AF_INET,
    'v6': socket.AF_INET6,
# 'file': socket.AF_UNIX,
}

SOCKET_KIND = {
    'tcp': socket.SOCK_STREAM,
    'udp': socket.SOCK_DGRAM,
#   'raw': socket.SOCK_RAW,
}

def sock_create(v4_v6, tcp_udp):
    #  import socket;help(socket)

    #  AddressFamily(value, names=None, *, module=None, qualname=None, type=None, start=1)
    #  AF_INET = <AddressFamily.AF_INET: 2>
    #  AF_INET6 = <AddressFamily.AF_INET6: 30>
    #  AF_UNIX = <AddressFamily.AF_UNIX: 1>

    v4_v6 = v4_v6.lower()

    try:
        af = ADDRESS_FAMILY[v4_v6]
    except KeyError as err:
        if err.args[0] != v4_v6:
            raise err
        logger.error(f"\"{v4_v6}\" is inappropriate as v4_v6.")
        return None

    #  SocketKind(value, names=None, *, module=None, qualname=None, type=None, start=1)
    #  SOCK_DGRAM = <SocketKind.SOCK_DGRAM: 2>
    #  SOCK_STREAM = <SocketKind.SOCK_STREAM: 1>

    #  Data descriptors defined here:
    #  family
    #      the socket family
    #
    #  proto
    #      the socket protocol
    #
    #  timeout
    #      the socket timeout
    #
    #  type
    #      the socket type

    tcp_udp = tcp_udp.lower()

    try:
        sk = SOCKET_KIND[tcp_udp]
    except KeyError as err:
        if err.args[0] != tcp_udp:
            raise err
        logger.error(f"\"{tcp_udp}\" is inappropriate as tcp_udp.")
        return None

    sock = socket.socket(af, sk)

    return sock

def sock_make_addr(host, port):

    if host and port in range(1, 65535 + 1):
        return (host, port)

    return None

def sock_make(sock, host, port, v4_v6=None, tcp_udp=None):

    addr = sock_make_addr(host, port)
    if not addr:
        return None

    if not sock:
        sock = sock_create(v4_v6, tcp_udp)
        if not sock:
            return None

    return sock

def sock_bind(sock, host, port, v4_v6=None, tcp_udp=None):
    result = False

    addr = (host, port)

    if sock is None:
        sock = sock_create(v4_v6, tcp_udp)
        if sock is None:
            return (None, addr, result)

    error = None
    try:
        sock.bind(addr)
        result = True
    except socket.timeout as err:
        error = err
    except socket.error as err:
        if err.args in (
            (98, 'Address already in use',),
            (13, 'Permission denied',),
            ('getsockaddrarg: port must be 0-65535.',),
            ):
            pass
        else:
            raise err
        error = err
    except TypeError as err:
        if err.args in (
            ('str, bytes or bytearray expected, not NoneType',),
            ('an integer is required (got type NoneType)',),
            ):
            pass
        else:
            raise err
        error = err
    except OverflowError as err:
      # getsockaddrarg: port must be 0-65535.
        error = err

    if error:
        logger.error(f'cannot bind{addr}. reason={error.args}')

    return (sock, addr, result)

def sock_connect(sock, host, port, v4_v6=None, tcp_udp=None):

    addr = sock_make_addr(host, port)
    if not addr:
        return None

    if not sock:
        sock = sock_create(v4_v6, tcp_udp)
        if not sock:
            return None

    try:
        sock.connect(addr)
    except ConnectionRefusedError as err:
        # err.args[0] ==  61
        if err.args[1] == 'Connection refused':
            pass
        else:
            sock.close()
            raise err

    return sock

def sock_send(tcp_sock, data):
    try:
        result = tcp_sock.sendall(data)
    except socket.timeout as e:
        logger.info(f"{tcp_sock}.sendall() got timeout.")
        return False
    return True

def sock_recv(tcp_sock, buf_size):
    try:
        recved_data = tcp_sock.recv(buf_size)
    except socket.timeout:
        logger.info(f"{tcp_sock}.recv({buf_size}) got timeout.")
        recved_data = None

    return recved_data

def addr_on_localhost(addr):
    if addr[0] in ('localhost', '127.0.0.1'):
        logger.info(f'addr={addr} is on localhost.')
        return True
    else:
        logger.info(f'addr={addr} is not on localhost.')
        return False

def get_host_port(host_port):
    sp = host_port.split(':')
    host = sp[0]
    port = int(sp[1])
    return host, port

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

def get_client_db_path(simulation_time, client_id):
    client_n_db = re.sub(ATAT_N, str(client_id), CLIENT_N_DB)
    return os.path.join(get_simulation_dir_path(simulation_time), client_n_db)

def get_simulation_dir_path(simulation_time):
    simulation_dir_path = re.sub(ATAT_SIMULATION_TIME,
                                 simulation_time.get_y15s(),
                                 SIMULATION_DIR_PATH)

    return simulation_dir_path

def get_simulation_db_path(simulation_time):
    simulation_dir_path = get_simulation_dir_path(simulation_time)
    simulation_db_path = os.path.join(simulation_dir_path,
                                      SIMULATION_DB)
    return simulation_db_path

def get_simulation_schema_path(simulation_time):
    simulation_dir_path = get_simulation_dir_path(simulation_time)
    simulation_schema_path = os.path.join(simulation_dir_path,
                                          SIMULATION_SCHEMA)

    return simulation_schema_path

def get_root_path():
    return UMATOBI_ROOT_PATH

def set_simulation_schema(simulation_time):
    simulation_dir_path = get_simulation_dir_path(simulation_time)
    simulation_schema_path = get_simulation_schema_path(simulation_time)

    if not os.path.isfile(simulation_schema_path):
        make_simulation_dir(simulation_dir_path)
        logger.info(f"shutil.copyfile(SIMULATION_SCHEMA_ORIG={SIMULATION_SCHEMA_ORIG}, simulation_schema_path={simulation_schema_path})")
        shutil.copyfile(SIMULATION_SCHEMA_ORIG, simulation_schema_path)

    return simulation_schema_path

def get_master_palm_path(simulation_time):
    y15s = SimulationTime.time_to_y15s(simulation_time)
    return os.path.join(re.sub(ATAT_SIMULATION_TIME, y15s, SIMULATION_DIR_PATH), MASTER_PALM)

def make_simulation_dir(simulation_dir_path):
    if not os.path.isdir(simulation_dir_path):
        os.makedirs(simulation_dir_path)
        logger.info(f"os.makedirs('{simulation_dir_path}')")

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
