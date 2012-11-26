import sys, os
import threading
import queue
import pickle

from simulator.node import Node
import simulator.sql
from lib import make_logger

class Darkness(object):
    '''漆黒の闇'''

    def __init__(self, **kwargs):
        '''\
        Darkness process 内で 多数の node thread を作成する。
        Client が leave_there を signal 状態にしたら終了処理を行う。
        '''

        # db_dir darkness_id client_id first_node_id
        # num_nodes log_level
        # made_nodes # share with client and darknesses
        # leave_there # share with client and another darknesses
        for attr, value in kwargs.items():
            # ここでは、logger を使えない。
            setattr(self, attr, value)
          # print(self, attr, value)

        self.logger = make_logger(self.db_dir, 'darkness',
                                  self.id, self.log_level)
        # ここより下からloggerを使えるようになる。
        self.logger.info(('{} initilized, '
                          'num_nodes={}.').format(self, self.num_nodes))
        self.logger.debug('{} debug log test.'.format(self))

        self.client_db_path = os.path.join(self.db_dir,
                                     'client.{}.db'.format(self.client_id))
        self.schema_path = \
            os.path.join(os.path.dirname(__file__), 'simulation_tables.schema')

        self._queue_darkness = queue.Queue()

        self.good_bye_with_nodes = threading.Event()

        self.nodes = []

    def start(self):
        '''\
        simulation 開始。
        simulation に必要な node thread を多数作成する。
        node thread 作成後、Client が leave_there を
        signal 状態にするまで待機し続ける。
        '''
        self.client_db = simulator.sql.SQL(owner=self,
                                           db_path=self.client_db_path,
                                           schema_path=self.schema_path)
        self.client_db.create_db()
        self.logger.info('{} client_db.create_db().'.format(self))

        for i in range(self.num_nodes):
            id = self.first_node_id + i
            host, port = 'localhost', 10000 + id
            node_ = Node(host, port, id,
                         self.good_bye_with_nodes,
                         self._queue_darkness
                         )
            self.logger.info('{} created {}.'.format(self, node_))
            node_.start()
            self.nodes.append(node_)

        self.made_nodes.value = len(self.nodes)
        if self.made_nodes.value == 1:
            msg = '{} made a node.'.format(self)
        else:
            msg = '{} made {} nodes.'.format(self, self.made_nodes.value)
        self.logger.info(msg)

        self.leave_there.wait()
        self.logger.info(('{} got leave_there signal.').format(self))
        self.logger.info(('{} set good_bye_with_nodes signal.').format(self))
        self.good_bye_with_nodes.set()

        for node_ in self.nodes:
            node_.join()
            self.logger.info('{} thread joined.'.format(node_))

        # _queue_darkness に残っている queue を全て吸い出し。
        self.inhole_queues_from_nodes()

        self.client_db.close()
        self.logger.info('{} client_db.close().'.format(self))

    def inhole_queues_from_nodes(self):
        queue_size = self._queue_darkness.qsize()
        self.logger.info('{} queue_size={}.'.format(self, queue_size))
        pickle_record = {}
        pickle_record['id'] = None
        for i in range(queue_size):
            pickled = self._queue_darkness.get()
            pickle_record['pickle'] = pickled
            self.client_db.insert('pickles', pickle_record)
          # d = pickle.loads(pickled)
          # self.logger.info('{}.get() i={} d="{}" pickled="{}"'.format(self, i, d, pickled))
      # client の db.pickles へ pickle 情報を commit
        self.client_db.commit()
        records = self.client_db.select('pickles', 'id,pickle',
                                        conditions='where id = 1')
        self.logger.info('records = "{}"'.format(records))

    def stop(self):
        '''simulation 終了'''
        for i in range(self.num_nodes):
            self.logger.info('stop node i={}'.format(i))

    def __str__(self):
        return 'Darkness(id={})'.format(self.id)
