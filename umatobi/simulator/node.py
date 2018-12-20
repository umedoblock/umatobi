import sys, os, threading
import struct
import math, random
import pickle, socketserver
import datetime

from umatobi.log import *
from umatobi.constants import *
import umatobi.p2p.core
from umatobi.lib import formula, validate_kwargs
from umatobi.lib.formula import _key_hex
from umatobi.lib import y15sformat_parse, elapsed_time
from umatobi.lib import get_master_hand_path
from umatobi.lib import dict2json, json2dict

# NodeUDPOffice and NodeOpenOffice classes are on different thread.
class NodeOpenOffice(threading.Thread):
    def __init__(self, node):
        threading.Thread.__init__(self)
        logger.info(f"NodeOpenOffice(self={self}, node={node})")
        self.node = node
        self.in_serve_forever = threading.Event()

    def run(self):
        # Create the server, binding to localhost on port ???
        logger.info(f"{self}")
        with NodeUDPOffice(self.node) as node_udp_office:
            logger.info(f"with NodeUDPOffice(node={self.node}, node_udp_office={node_udp_office})")
            self.node.node_udp_office = node_udp_office
            # NodeOpenOffice() run on different thread of NodeUDPOffice.
            logger.info("node_udp_office.serve_forever()")
            node_udp_office.serve_forever()
        logger.info(f"{self} end!")

class NodeUDPOffice(socketserver.UDPServer):
    def __init__(self, node):
        logger.info(f"NodeUDPOffice(self={self}, node={node})")

        self.node = node
        self.clients = []
    #   self.server in NodeOffice class means NodeUDPOffice instance.
        self._determine_office_addr()

    def _determine_office_addr(self):
        logger.info(f"node_office_addr={self.node.node_office_addr}")
        host, port = self.node.node_office_addr

        ports = list(range(1024, 65536))
        random.shuffle(ports)
        while True:
            try:
                port = ports.pop()
            except IndexError as e:
                raise RuntimeError("every ports are in use.")
            addr = (host, port)

            try:
                super().__init__(addr, NodeOffice)
            except OSError as oe:
              # [Errno 98] Address already in use
                if oe.errno != 98:
                    raise(oe)
                continue
            break

        # node_office_addr が決定されている。
        with self.node.office_door:
            self.node.node_office_addr = addr

        logger.info(f"{self}.node.addr={addr}")

    def serve_forever(self):
        self.node.node_open_office.in_serve_forever.set()
        super().serve_forever()

class NodeOffice(socketserver.DatagramRequestHandler):
    def handle(self):
        logger.info(f"""{self}.handle()
        self.request={self.request} # socket.SOCK_DGRAM
        self.client_address={self.client_address} # ('localhost', 11111)
        self.server={self.server} # RequestHandler
        self.socket={self.socket}
        """)
    #   self.server in NodeOffice class means NodeUDPOffice instance.
        text_message = self.rfile.readline().decode().strip()
        logger.info(f"text_message={text_message}")
        logger.info(f"type(text_message)={type(text_message)}")
        self.server.clients.append(self)

        sheep = json2dict(text_message)
        logger.info(f"sheep={sheep}")
        professed = sheep['profess']
        logger.info(f"professed={professed}")

        if professed == 'You are Red.':
            client_addr = self.client_address

            hop = sheep['hop']
            with self.server.node.office_door:
                self.server.node.nodes.extend(client_addr)
            d = {
                'profess': 'You are Green.',
                'hop': hop * 2,
            }
            reply = dict2json(d).encode('utf-8')
        else:
            reply = b'Go back home.'
            logger.error(f"unknown professed='{professed}', text_message={text_message}")
        logger.info(f"client_address={self.client_address}, reply={reply}")
        self.wfile.write(reply)

 #  def finish(self):
 #      logger.info(f"finish()")

    def finish(self):
        logger.info(f"finish()")
        super().finish()

  # echo server
  # def handle(self):
  #     got_packet = self.rfile.read()
  #     self.wfile.write(got_packet.upper())
  # def finish(self):
  #     super().finish()

class Node(umatobi.p2p.core.Node):

    _output = print

    def __init__(self, **kwargs):
        '''\
        simulator 用 node を初期化する。
        '''
        st_barrier = set([
            'host', 'port', 'id', 'start_up_time',
            'byebye_nodes', '_queue_darkness'
        ])

        validate_kwargs(st_barrier, kwargs)
        super().__init__(kwargs['host'], kwargs['port'])
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        self._rad, self._x, self._y = 0.0, 0.0, 0.0
        self.node_office_addr = ('localhost', 0)
        self.nodes = []
        self.office_door = threading.Lock()
        self.node_office_addr_assigned = threading.Event()
        self.master_hand_path = get_master_hand_path(SIMULATION_DIR, self.start_up_time)

    def run(self):
        self._open_office()
        d = self._init_node()
        et = elapsed_time(y15sformat_parse(self.start_up_time))
        self.to_darkness(d, et)

        self._steal_master_palm()
        self.regist()

        logger.info(f"byebye_nodes.wait()")
        self.byebye_nodes.wait()
        logger.info(f"release_clients()")
        self.release_clients() # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        logger.info(f"node_udp_office.shutdown()")
        self.node_udp_office.shutdown() # close node office !!!!!!!!!!!!!!!!!!
        self.node_open_office.join() # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        logger.info(f"byebye_nodes leave !")

    def _open_office(self):
        logger.info(f"")
        node_open_office = NodeOpenOffice(self)
        self.node_open_office = node_open_office
        logger.info(f"{self}.open_office(), node_open_office.start()")
        node_open_office.start()
        # wait a minute
        # to set node_open_office instance
        # to node instance
        # in NodeOpenOffice.run()
        logger.info(f"node_open_office.wait()")
        node_open_office.in_serve_forever.wait()
        self.host, self.port = self.node_office_addr
        self.node_office_addr_assigned.set()
        logger.info(f"node_open_office={node_open_office}")
        # node.node_office_addr が決定している。
        return node_open_office

    def regist(self):
        logger.info(f"regist(), master_hand_path={self.master_hand_path}")
        os.makedirs(os.path.dirname(self.master_hand_path), exist_ok=True)
        with open(self.master_hand_path, 'a') as master:
            node_info = f"{self.host}:{self.port}:{self.key_hex}" + '\n'
            print(node_info, end='', file=master)
      # msg = 'I am Node.'
      # recver_addr = ('localhost', 222)
      # self.sock.sendto(msg, recver_addr)
      # recved_msg, who = self.sock.recvfrom(1024)

    def _steal_master_palm(self):
        if not os.path.isfile(self.master_hand_path):
            logger.info(f"not found 'master_hand_path={self.master_hand_path}'")
            return None

        logger.info(f"found 'master_hand_path={self.master_hand_path}'")
        with open(self.master_hand_path) as master_palm:
            node_lines = master_palm.read()
        return node_lines

    def _force_shutdown(self):
        self.disappear()

    def _init_node(self):
      # print('{} started.'.format(self))
        d = {}
        d['id'] = self.id
        d['host'] = self.host
        d['port'] = self.port

        self.update_key()
        key_hex = self._key_hex()
      # print('{} key_hex = {}'.format(self, key_hex))
        _keyID = int(key_hex[:10], 16)
        rad, x, y = formula._key2rxy(_keyID)

        d['key_hex'] = key_hex
        d['rad'] = rad
        d['x'] = x
        d['y'] = y
        d['status'] = 'active'

        return d

    def to_darkness(self, obj, et):
        pds = pickle.dumps(obj)
        tup = (et, pds)
        self._queue_darkness.put(tup)

    def appear(self):
        super().appear()

    def disappear(self):
        super().disappear()

    def release_clients(self):
        logger.info(f"{self} clients={self.node_udp_office.clients}")
        for node_office_client in self.node_udp_office.clients:
            node_office_client.byebye()

    def __str__(self):
        return 'Node(id={})'.format(self.id)

    def update_key(self, k=b''):
        '''\
        how to mapping ? key to circle.
        key は '0' * 16 から 'f' * 16 までの範囲の値です。
        key は 0 時をゼロとして時計回り順で増加していきます。
        つまり、時計の時間と Key の値の関係は以下の通りです。
         0 時: 0000000000000000
         3 時: 4000000000000000
         6 時: 8000000000000000
         9 時: c000000000000000
        12 時: ffffffffffffffff
        '''
        super().update_key(k=k)

        self.key_hex = _key_hex(self.key)
        self._keyID = struct.unpack('>I', self.key[:4])[0]
        r, x, y = formula._key2rxy(self._keyID)
        self._rad, self._x, self._y = r, x, y

    def get_status(self, type_='dict'):
        'node の各種情報を表示。'
        super().get_status(type_)
        self._status['_keyID'] = self._keyID

      # self._status['_rad.float'] = '{:.3f} * PAI'.format(self._rad / math.pi)
        key_rate = (self._keyID / (1 << 32))
        hour, mod = divmod(key_rate, 1 / 12)
        self._status['_rad.hour'] = '({} / 12 + {:.3f}) * 2 * PAI'.format(int(hour), mod)
        self._status['_x'] = self._x
        self._status['_y'] = self._y

        return self._status
