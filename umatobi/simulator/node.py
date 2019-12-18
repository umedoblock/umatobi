# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import sys, os, threading, struct, math, random, pickle, socketserver, datetime

from umatobi.simulator.core.key import Key
from umatobi.log import *
from umatobi.constants import *
from umatobi.simulator.core import node
from umatobi.lib import *

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
              # Address already in use
                if oe.args[1] == 'Address already in use':
                    continue
                else:
                    raise(oe)
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

    TO_DARKNESS = set(('id', 'office_addr', 'key', 'status', 'path_maker'))

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
        self.simulation_time = self.path_maker.simulation_time

        self.key = Key()
        self.status = 'active'

        self.nodes = []
        self.im_ready = threading.Event()
        self.office_door = threading.Lock()
        self.office_addr_assigned = threading.Event()

        self.master_palm_txt_path = self.path_maker.get_master_palm_txt_path()

    def run(self):
        self._open_office()
        et = self.get_elapsed_time()
        d_attrs = self.get_attrs()
        self.put_on_darkness(d_attrs, et)

        self._steal_a_glance_at_master_palm()
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
        return f"{':'.join(map(str, self.office_addr))}:{self.key}" + '\n'

    def regist(self):
        logger.info(f"regist(), master_palm_path={self.master_palm_path}")
        os.makedirs(os.path.dirname(self.master_palm_path), exist_ok=True)
        with open(self.master_palm_path, 'a') as master:
            print(self.get_info(), end='', file=master)
      # msg = 'I am Node.'
      # recver_addr = ('localhost', 222)
      # self.sock.sendto(msg, recver_addr)
      # recved_msg, who = self.sock.recvfrom(1024)
        self.im_ready.set()

    def _steal_a_glance_at_master_palm(self):
        if not os.path.isfile(self.master_palm_path):
            logger.info(f"not found 'master_palm_path={self.master_palm_path}'")
            return None

        logger.info(f"found 'master_palm_path={self.master_palm_path}'")
        with open(self.master_palm_path) as master_palm:
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
            keys = self.TO_DARKNESS
        d = {}
        for key in keys:
            d[key] = getattr(self, key)
        return d

    def put_on_darkness(self, obj, et):
        pds = pickle.dumps(obj)
        tup = (et, pds)
        self._queue_darkness.put(tup)

    def get_elapsed_time(self):
        return self.simulation_time.passed_ms()

    def appear(self):
        super().appear()

    def disappear(self):
        super().disappear()

    def release_clients(self):
        logger.info(f"{self} clients={self.node_udp_office.clients}")
        for node_office_client in self.node_udp_office.clients:
            node_office_client.byebye()

    def __str__(self):
        return 'Node(id={}, addr={})'.format(self.id, self.udp_addr)

    def update(self, k=b''):
        self.key.update(k)
