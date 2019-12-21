# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import threading, os, sys, socketserver, datetime, time, configparser, random
import sqlite3

from umatobi.log import *
from umatobi.constants import *
from umatobi.lib.simulation_time import *
from umatobi.lib import *
import umatobi.simulator.sql
from umatobi import simulator

# WatsonTCPOffice and WatsonOpenOffice classes are on different thread.
class WatsonOpenOffice(threading.Thread):
    def __init__(self, watson):
        threading.Thread.__init__(self)
        logger.info(f"WatsonOpenOffice(self={self}, watson={watson})")
        self.watson = watson
        self.in_serve_forever = threading.Event()

    def run(self):
        # Create the server, binding to localhost on port ???
        logger.info(f"{self}.run()")
        with WatsonTCPOffice(self.watson) as watson_tcp_office:
            logger.info(f"{self}.run(), with WatsonTCPOffice(watson={self.watson}, watson_tcp_office={watson_tcp_office})")
            self.watson.watson_tcp_office = watson_tcp_office
            # WatsonOpenOffice() run on different thread of WatsonTCPOffice.
            self.in_serve_forever.set()
            self.watson.watson_office_addr_assigned.set()
            logger.info(f"{self}.run(), watson_tcp_office.serve_forever()")
            watson_tcp_office.serve_forever()
        logger.info(f"{self}.run() end!")
        watson_tcp_office.server_close()

# WatsonTCPOffice and WatsonOffice classes are on same thread.
class WatsonTCPOffice(socketserver.TCPServer):
    def __init__(self, watson):
        logger.info(f"WatsonTCPOffice(self={self}, watson={watson})")

        self.watson = watson
        self.clients = []
    #   self.server in WatsonOffice class means WatsonTCPOffice instance.
        self.simulation_time = watson.simulation_time
        self.simulation_db = simulator.sql.SQL(db_path=watson.simulation_db_path)
        logger.info(f"{self}.simulation_db.access_db(), db_path={watson.simulation_db_path}")
        self.simulation_db.access_db()

        self._determine_office_addr()

    def _determine_office_addr(self):
        logger.info(f"watson_office_addr={self.watson.watson_office_addr}")
        host, port = self.watson.watson_office_addr
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
                super().__init__(addr, WatsonOffice)
            except OSError as oe:
                if oe.errno != 98:
                    raise(oe)
                continue
            break

        # watson_office_addr が決定されている。
        logger.info(f"{self}.watson.watson_office_addr={addr}")
        self.watson.watson_office_addr = addr

    def shutdown_request(self, request):
        pass

class WatsonOffice(socketserver.StreamRequestHandler):
  # class BaseRequestHandler:
  #     def __init__(self, request, client_address, server):
  # class StreamRequestHandler(BaseRequestHandler):
  # ...

  # BaseRequestHandler instance calls
  # setup(), handle() and finish() in __init__()
  # after it sets request, client_address, server as like a below

    def setup(self):
        super().setup()

        try:
            self.sheep = bytes2dict(self.rfile.readline())
        except BaseException as err:
            self.professed = f'invalid sheep came. error="{err}"'
            self.err = err
            return

        logger.info(f"sheep={self.sheep}")
        if set(self.sheep.keys()) == set(('profess', 'num_nodes')):
            self.professed = self.sheep['profess']
            self.num_nodes = self.sheep['num_nodes']
        else:
            self.professed = 'sheep doesn\'t profess.'
            self.num_nodes = -1

    def handle(self):
        logger.info(f"""{self}.handle()
        request={self.request} # socket.SOCK_STREAM
        client_address={self.client_address} # ('localhost', 11111)
        server={self.server} # RequestHandler
        """)

        if self.professed == 'I am Client.':
            self.consult_orig = SimulationTime()
            self.client_id = len(self.server.clients)
            self.server.clients.append(self)
            self.node_index = self.server.watson.total_nodes
            self.server.watson.total_nodes += self.num_nodes

            logger.info(f"""
            client_id={self.client_id},
            client_address={self.client_address},
            node_index={self.node_index}.
            """)

            self.insert_client_record()

            client_reply = self.make_client_reply()
            logger.info(f"total_nodes={self.server.watson.total_nodes}.")
        else:
            logger.error(f"unknown professed='{self.professed}'")
            client_reply = b'Go back home.'

        self.client_reply = client_reply
        logger.info(f"client_reply={client_reply}")

    def finish(self):
        logger.info(f"{self}.finish()")
        self.wfile.write(self.client_reply)
        # avoid to call
        # StreamRequestHandler.wfile.flush()
        # StreamRequestHandler.wfile.close()
        # StreamRequestHandler.rfile.close()
        # in
        # StreamRequestHandler.finish()

    # WatsonOffice original

    def make_client_record(self):
        addr = ':'.join(str(x) for x in self.client_address)
        client_record = {
            'id': self.client_id,
            'addr': addr,
            'consult_iso8601': self.consult_orig.get_iso8601(),
            'thanks_iso8601': None,
            'num_nodes': self.num_nodes,
            'node_index': self.node_index,
            'log_level': self.server.watson.log_level,
        }
        logger.debug(f"client_record={client_record}")
        return client_record

    def insert_client_record(self):
        client_record = self.make_client_record()
        sql = self.server.simulation_db.insert('clients', client_record)
        logger.debug(f"sql={sql}")
        self.server.simulation_db.commit()

    def make_client_reply(self):
        self.d_client_reply = {
            'client_id': self.client_id,
            'start_up_iso8601': self.server.simulation_time.get_iso8601(),
            'node_index': self.node_index,
            'log_level': self.server.watson.log_level,
        }
        logger.debug(f"d_client_reply={self.d_client_reply}")
        client_reply = dict2bytes(self.d_client_reply)
        return client_reply

    def byebye(self):
        logger.info(f"{self}.byebye()")
        # call StreamRequestHandler.finish()
        super().finish()

class Watson(threading.Thread):
    MAX_NODE_NUM=8

    def __str__(self):
        return f"Watson{self.watson_office_addr}"

    def __init__(self, watson_office_addr, simulation_seconds, simulation_time, log_level):
        '''\
        watson: Cient, Node からの TCP 接続を待つ。
        起動時刻を start_up_time と名付けて記録する。
        '''
        threading.Thread.__init__(self)

        self.simulation_time = simulation_time
        self.path_maker = PathMaker(self.simulation_time)
        self.open_office_orig = None
        self.close_office_orig = None
        self.end_up_orig = None

        self.simulation_seconds = simulation_seconds
        self.watson_office_addr = watson_office_addr
        self.total_nodes = 0

        self.log_level = log_level

        logger.info(f"Watson(self={self}, watson_office_addr={watson_office_addr}, simulation_seconds={simulation_seconds}, simulation_time={simulation_time}, log_level={log_level}))")

        self.path_maker.make_simulation_dir()

        self.simulation_dir_path = self.path_maker.get_simulation_dir_path()
        self.simulation_db_path = self.path_maker.get_simulation_db_path()
        self.simulation_schema_path = self.path_maker.set_simulation_schema()
        logger.info(f"Watson(self={self}, simulation_dir_path={self.simulation_dir_path}, simulation_db_path={self.simulation_db_path}, simulation_schema_path={self.simulation_schema_path})")

        self.watson_office_addr_assigned = threading.Event()
        self.timeout_sec = 1
        self.nodes = []

    def run(self):
        '''simulation 開始'''
        logger.info(f"{self}.run()")

        self.touch_simulation_db_on_clients()
        self.open_office()

        self.relaxing()

        self.release_clients()

        # close watson office
        logger.info(f"{self}.run(), {self}.watson_tcp_office.shutdown()")
        self.watson_tcp_office.shutdown()

      # self._wait_tcp_clients()
        logger.info(f"{self}.run(), {self}._wait_client_db()")
        self._wait_client_db()

        # simulation_db に骨格を作成する。
        # simulation も終わるってのにねぇ。
        logger.info(f"{self}.simulation_db.access_db()")
        self.simulation_db.access_db()
        self._merge_db_to_simulation_db()
        self._create_simulation_table()
        self._construct_simulation_table()
        logger.info(f"{self}.simulation_db.close()")
        self.simulation_db.close()

    def touch_simulation_db_on_clients(self):
        self.touch_simulation_db()

        self.simulation_db.access_db()
        self.touch_clients_table()

    def touch_simulation_db(self):
        logger.info(f"{self}.touch_simulation_db_on_clients()")
        logger.debug(f"{self}.touch_simulation_db_on_clients(), simulation_db_path={self.simulation_db_path}, simulation_schema_path={self.simulation_schema_path}")
        self.simulation_db = simulator.sql.SQL(
                                db_path=self.simulation_db_path,
                                schema_path=self.simulation_schema_path)
        logger.info(f"{self}.touch_simulation_db_on_clients(), simulation_db={self.simulation_db}")
        logger.info(f"{self}.simulation_db.create_db()")
        self.simulation_db.create_db()
#       logger.info(f"{self}.simulation_db.create_table('clients')")

        # この後，WatsonTCPOffice が simulation_db に access する。
        # sqlite3 では， sqlite3.connect(self.db_path) の返す instance を
        # 作成した thread と別の thread では使えないので，一度閉じている。
        logger.info(f"{self}.simulation_db.close()")
        self.simulation_db.close()

    def touch_clients_table(self):
        self.simulation_db.create_table('clients')
        # この後，WatsonTCPOffice が simulation_db に access する。
        # sqlite3 では， sqlite3.connect(self.db_path) の返す instance を
        # 作成した thread と別の thread では使えないので，一度閉じている。

    def open_office(self):
        logger.info(f"{self}.open_office()")
        watson_open_office = WatsonOpenOffice(self)
        self.watson_open_office = watson_open_office
        logger.info(f"{self}.open_office(), watson_open_office.start()")
        watson_open_office.start()
        # wait a minute
        # to set watson_open_office instance
        # to watson instance
        # in WatsonOpenOffice.run()
        logger.info(f"{self}.open_office(), watson_open_office.wait()")
        watson_open_office.in_serve_forever.wait()
        logger.info(f"{self}.open_office(), watson_open_office={watson_open_office}")
        # watson.watson_office_addr が決定している。
        return watson_open_office

    def relaxing(self):
        passed_seconds = self.simulation_time.passed_seconds()
        relaxing_time = self.simulation_seconds - passed_seconds

        logger.info(f"{self}.relaxing(), relaxing_time={relaxing_time}")
        logger.debug(f"{self}.relaxing(), simulation_seconds={self.simulation_seconds}, start_up_iso8601={self.simulation_time.get_iso8601()}, passed_seconds={passed_seconds}")
        time.sleep(relaxing_time)

    def release_clients(self):
        '''\
        watsonが把握しているClientに "break down" を送信し、
        各Clientに終了処理を行わせる。
        Clientは、終了処理中に client.N.db を送信してくる。
        '''
        logger.info(f"{self}.release_clients(), watson_tcp_office.client={self.watson_tcp_office.clients}")
        result = b'break down.'
        for watson_office_client in self.watson_tcp_office.clients:
            logger.info(f"{self}.release_clients(), watson_office_client={watson_office_client}")
            watson_office_client.wfile.write(result)
            watson_office_client.byebye()

    def _wait_client_db(self):
        logger.info(f"""{self}._wait_client_db(),
                      {self}, は、client.N.dbの回収に乗り出した。
                      {self}, なんて言いながら実は待機してるだけ。
                      {self}, client.N.dbの回収完了。""")

    def _merge_db_to_simulation_db(self):
        logger.info(f"""{self}._merge_db_to_simulation_db(),
                              client.N.db の結合開始。
                              client.N.db の結合終了。""")

    def _create_simulation_table(self):
        logger.info(f"{self}._create_simulation_table()")
        self.simulation_db.create_table('simulation')

    def _construct_simulation_table(self):
        logger.info(f"{self}._construct_simulation_table()")
        d_simulation = {}
        d_simulation['title'] = UMATOBI_SIMULATION_DIR

        d_simulation['start_up_iso8601'] = str(self.simulation_time)
        d_simulation['close_office_iso8601'] = str(self.close_office_orig)
        d_simulation['end_up_iso8601'] = str(self.end_up_orig)
        d_simulation['open_office_iso8601'] = str(self.open_office_orig)

        d_simulation['simulation_seconds'] = self.simulation_seconds
        d_simulation['watson_office_addr'] = \
                '{}:{}'.format(*self.watson_office_addr)
        d_simulation['total_nodes'] = self.total_nodes
        d_simulation['n_clients'] = len(self.watson_tcp_office.clients)

        d_simulation['memo'] = 'なにかあれば'
        d_simulation['log_level'] = 'INFO'
        d_simulation['version'] = '0.0.0'

        logger.debug(f"{self}._construct_simulation_table(), d_simulation={d_simulation}")
        self.simulation_db.insert('simulation', d_simulation)
        self.simulation_db.commit()

        return d_simulation

    def join(self):
        '''watson threadがjoin'''
        logger.info(f"{self}.join()")
        threading.Thread.join(self)
        logger.debug('watson thread joined.')
