import json, datetime, time, os, threading, sched, configparser, socket

from umatobi.constants import *
from umatobi.log import *

class Polling(threading.Thread):
    def __init__(self, polling_secs):
        threading.Thread.__init__(self)
        self.polling_secs = polling_secs
        # class sched.scheduler(timefunc, delayfunc)
        self._sche = sched.scheduler(time.time, time.sleep)
        self._sche.enter(self.polling_secs, 1, self._polling, ())

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

def sock_create(v4_v6, tcp_udp):
    #  import socket;help(socket)

    #  AddressFamily(value, names=None, *, module=None, qualname=None, type=None, start=1)
    #  AF_INET = <AddressFamily.AF_INET: 2>
    #  AF_INET6 = <AddressFamily.AF_INET6: 30>
    #  AF_UNIX = <AddressFamily.AF_UNIX: 1>

    address_family = {
        'v4': socket.AF_INET,
        'v6': socket.AF_INET6,
#     'file': socket.AF_UNIX,
    }
    v4_v6 = v4_v6.lower()

    try:
        af = address_family[v4_v6]
    except KeyError as err:
        if err.args[0] != v4_v6:
            raise err
        logger.error(f"\"{v4_v6}\" is inappropriate as v4_v6.")
        return None

    #  SocketKind(value, names=None, *, module=None, qualname=None, type=None, start=1)
    #  SOCK_DGRAM = <SocketKind.SOCK_DGRAM: 2>
    #  SOCK_STREAM = <SocketKind.SOCK_STREAM: 1>

    socket_kind = {
        'tcp': socket.SOCK_STREAM,
        'udp': socket.SOCK_DGRAM,
#       'raw': socket.SOCK_RAW,
    }

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
        sk = socket_kind[tcp_udp]
    except KeyError as err:
        if err.args[0] != tcp_udp:
            raise err
        logger.error(f"\"{tcp_udp}\" is inappropriate as tcp_udp.")
        return None

    tcp_sock = socket.socket(af, sk)

    return tcp_sock

def sock_send(tcp_sock, data):
    try:
        result = tcp_sock.sendall(data)
    except socket.timeout as e:
        logger.info(f"{self.tcp_sock} got timeout.")
        return False
    return True

def sock_recv(tcp_sock, buf_size):
    try:
        recved_data = tcp_sock.recv(buf_size)
    except socket.timeout:
        recved_data = None

    return recved_data

def are_on_the_same_network_endpoint(You, I):
    if You[0] == I[0]:
        logger.info(f"You(={You}) and I(={I}) refer to the same network endpoint.")
        return True
    else:
        logger.info(f"You(={You}) and I(={I}) refer to the same network endpoint.")
        return False

def get_host_port(host_port):
    sp = host_port.split(':')
    host = sp[0]
    port = int(sp[1])
    return host, port

def get_db_from_schema():
    db = configparser.ConfigParser()
    with open(SCHEMA_PATH, encoding='utf-8') as schema:
        db.read_file(schema)
  # print('db =', db)
  # print('db.sections =', db.sections)
  # print('tuple(db.sections()) =', tuple(db.sections()))
  # db.keys() = ('DEFAULT', 'simulation', 'nodes', 'clients', 'growings')
    return db

def get_table_columns(table_name):
    return get_db_from_schema()[table_name]

def get_master_hand(start_up_orig):
    start_up_time = make_start_up_time(start_up_orig)
    return os.path.join(start_up_time, MASTER_HAND)

def get_master_hand_path(simulation_dir, start_up_orig):
    return os.path.join(simulation_dir, get_master_hand(start_up_orig))

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

def datetime_now():
    return datetime.datetime.now()

def make_start_up_orig():
    start_up_orig = datetime_now()
    return start_up_orig

def make_start_up_time(start_up_orig=None):
    if not start_up_orig:
        start_up_orig = make_start_up_orig()
    start_up_time = y15sformat_time(start_up_orig)
    return start_up_time

def start_up_orig_to_isoformat(start_up_orig):
  # >>> datetime.datetime.isoformat(now)
  # '2019-08-27T02:43:20.708976'
    return datetime.datetime.isoformat(start_up_orig)

def isoformat_to_start_up_orig(isoformat):
  # >>> datetime.datetime.fromisoformat('2019-08-27T02:43:20.708976')
  # datetime.datetime(2019, 8, 27, 2, 43, 20, 708976)
    return datetime.datetime.fromisoformat(isoformat)

Y15S_FORMAT='%Y-%m-%dT%H%M%S'
def y15sformat_time(t):
    "'return time format '2012-11-02T232227'"
    return t.strftime(Y15S_FORMAT)

def current_y15sformat_time():
    now = datetime_now()
    return y15sformat_time(now)

def y15sformat_parse(s):
    return datetime.datetime.strptime(s, Y15S_FORMAT)

def get_passed_ms(start_up_orig):
    '''simulation 開始から現在までに経過したmilli秒数。'''
    now = datetime_now()
    # relativeCreated の時間単位がmsのため、
    # elapsed_time()もms単位となるようにする。
    return int(((now - start_up_orig) * 1000).total_seconds())

def elapsed_time(start_up_orig, now=None):
    '''simulation 開始から現在までに経過したmilli秒数。'''
    if not None:
        now = datetime_now()
    # relativeCreated の時間単位がmsのため、
    # elapsed_time()もms単位となるようにする。
    return int(((now - start_up_orig) * 1000).total_seconds())

def _normalize_ms(seconds):
    return int(seconds * 1000)

def get_passed_seconds(orig):
    e = datetime_now()
    return (e - orig).total_seconds()

def get_passed_ms(orig):
    passed_seconds = get_passed_seconds(orig)
    return _normalize_ms(passed_seconds)
