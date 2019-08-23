import sys, os, threading
import struct
import math, random
import pickle, socketserver
import datetime

from umatobi.log import *
from umatobi.constants import *
from umatobi.simulator.core import node
from umatobi.lib import formula, validate_kwargs
from umatobi.lib.formula import _key_hex
from umatobi.lib import y15sformat_parse, elapsed_time
from umatobi.lib import get_master_hand_path
from umatobi.lib import dict2bytes, bytes2dict

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
        self._determine_node_office_addr()

    def _determine_node_office_addr(self):
        logger.info(f"START {self}.node.office_addr={self.node.office_addr}")
        host = self.node.office_addr[0]

        ports = list(range(1024, 65536))
        random.shuffle(ports)
        while True:
            try:
                port = ports.pop()
            except IndexError as e:
                raise RuntimeError("every ports are in use.")
            addr = (host, port)

            try:
                # 以下で、bind() して帰ってくるので、
                # self.server_close() を忘れずに。
                super().__init__(addr, NodeOffice)
            except OSError as oe:
              # [Errno 98] Address already in use
                if oe.errno != 98:
                    raise(oe)
                continue
            break

        # office_addr が決定されている。
        with self.node.office_door:
            self.node.office_addr = addr

        logger.info(f" DONE {self}.node.office_addr={self.node.office_addr}")

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
        sheep = bytes2dict(self.rfile.readline())
        self.server.clients.append(self)

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
            reply = dict2bytes(d)
        else:
            reply = b'Go back home.'
            logger.error(f"unknown professed='{professed}', sheep={sheep}")
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

class Node(node.Node):

    ATTRS = ('id', 'office_addr', 'key', 'rad', 'x', 'y', 'status')

    def __init__(self, **kwargs):
        '''\
        simulator 用 node を初期化する。
        '''

        self.office_addr = (kwargs.get('host', None), kwargs.get('port', None))
        super().__init__(*self.office_addr)

        for attr, value in kwargs.items():
            if attr in ('host', 'port'):
                continue
            setattr(self, attr, value)

        self.update_key()
        key_hex = self._key_hex()
      # print('{} key_hex = {}'.format(self, key_hex))
        _keyID = int(key_hex[:10], 16)
        rad, x, y = formula._key2rxy(_keyID)

        self.key_hex = key_hex
        self.rad = rad
        self.x = x
        self.y = y
        self.status = 'active'

        self.nodes = []
        self.office_door = threading.Lock()
        self.office_addr_assigned = threading.Event()
        self.master_hand_path = get_master_hand_path(SIMULATION_DIR, self.start_up_time)

    def run(self):
        self._open_office()
        et = elapsed_time(y15sformat_parse(self.start_up_time))
        d_attrs = self.get_attrs()
        self.to_darkness(d_attrs, et)

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
        self.office_addr_assigned.set()
        logger.info(f"node_open_office={node_open_office}")
        # node.office_addr が決定している。
        return node_open_office

    def get_info(self):
        return f"{':'.join(map(str, self.office_addr))}:{self.key_hex}" + '\n'

    def regist(self):
        logger.info(f"regist(), master_hand_path={self.master_hand_path}")
        os.makedirs(os.path.dirname(self.master_hand_path), exist_ok=True)
        with open(self.master_hand_path, 'a') as master:
            print(self.get_info(), end='', file=master)
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

    def set_attrs(self, d={}):
        attrs = d
        for attr, value in attrs.items():
            setattr(self, attr, value)

    def get_attrs(self, keys=()):
        if not keys:
            keys = self.ATTRS
        d = {}
        for key in keys:
            d[key] = getattr(self, key)
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
        return 'Node(id={}, addr={})'.format(self.id, self.udp_ip)

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
        self._keyid = struct.unpack('>I', self.key[:4])[0]
        r, x, y = formula._key2rxy(self._keyid)

      # print('{} key_hex = {}'.format(self, key_hex))
        _keyID = int(key_hex[:10], 16)
        rad, x, y = formula._key2rxy(_keyID)

        self.key_hex = key_hex
        self.rad = rad
        self.x = x
        self.y = y
