import sys, os
import threading
import queue
import pickle

from simulator.node import Node
import simulator.sql
from lib import make_logger, validate_kwargs
from lib import Polling
from lib import SCHEMA_PATH

class ExhaleQueue(Polling):
    def __init__(self, polling_secs, darkness):
        Polling.__init__(self, polling_secs)

        self.darkness = darkness
        self.client_db_path = self.darkness.client_db_path
        self.client_db = self.darkness.client_db
        self.schema_path = self.darkness.schema_path
        self._queue_darkness = self.darkness._queue_darkness
        self.queue_size_total = 0
        self.logger = self.darkness.logger
        self.logger.info('{} created ExhaleQueue()'.format(self.darkness))

    def run(self):
        '''\
        sqlite3は、sqlite3.connet()を実行したthreadでのみ、commit(), select()
        などの操作を許可している。sqlite3.connet()を実行したthreadと
        別のthreadでcommit(), select()などを行うと例外が発生する。
        また、client_db.create_db()内で、sqlite3.connect()を実行している。
        その為、Polling.run()内でsched.Sched()を実行するthreadを走らせ、
        commit()も同時に行いたい場合、client_db.create_db()を実行するthreadと、
        Polling.run() を実行するthreadは同一threadである必要があり、
        run()内で、client_db.create_db()と、Polling.run()を行った。
        '''
        self.logger.info('{} run ExhaleQueue()'.format(self.darkness))
        self.client_db.create_db()
        self.logger.info('{} client_db.create_db().'.format(self.darkness))

        Polling.run(self)
        self.logger.info('{} queue_size_total={}'.format(self.darkness, self.queue_size_total))
        self.logger.info('{} stop ExhaleQueue()'.format(self.darkness))

    def is_continue(self):
        if self.darkness.all_nodes_inactive.is_set():
            self.inhole_queues_from_nodes()
            self.client_db.close()
            self.logger.info('{} client_db.close().'.format(self.darkness))
            return False
        else:
            return True

    def polling(self):
        self.inhole_queues_from_nodes()

    def inhole_queues_from_nodes(self):
        '''\
        _queue_darkness に残っている queue を一掃する。
        '''
        queue_size = self._queue_darkness.qsize()
        self.queue_size_total += queue_size
        self.logger.info('{} _queue_darkness.qsize()={}.'.format(self.darkness, queue_size))
        growing = {}
        growing['id'] = None
        for i in range(queue_size):
            et, pickled = self._queue_darkness.get()
            growing['elapsed_time'] = et
            growing['pickle'] = pickled
            self.client_db.insert('growings', growing)
      # client の db.growings へ pickle 情報を commit
        self.client_db.commit()
        growings = self.client_db.select('growings', 'id,pickle',
                                                conditions='')
        self.logger.debug('growings table dumped =\n"{}"'. \
                           format(growings))

class Darkness(object):
    '''漆黒の闇'''

    def __init__(self, **kwargs):
        '''\
        Darkness process 内で 多数の node thread を作成する。
        Client が leave_there を signal 状態にしたら終了処理を行う。
        '''
        st_barrier = set([
            'id', 'client_id', 'first_node_id',
            'dir_name', 'num_nodes', 'log_level', 'start_up_time',
            'made_nodes', # share with client and darknesses
            'leave_there', # share with client and another darknesses
        ])
        validate_kwargs(st_barrier, kwargs)

        for attr, value in kwargs.items():
            # ここでは、logger を使えない。
            setattr(self, attr, value)
          # print(self, attr, value)

        self.logger = make_logger(self.dir_name, 'darkness',
                                  self.id, self.log_level)
        # ここより下からloggerを使えるようになる。
        self.logger.info(('{} initilized, '
                          'num_nodes={}.').format(self, self.num_nodes))
        self.logger.debug('{} debug log test.'.format(self))

        self.client_db_path = os.path.join(self.dir_name,
                                     'client.{}.db'.format(self.client_id))
        self.schema_path = SCHEMA_PATH
        self.client_db = simulator.sql.SQL(db_path=self.client_db_path,
                                           schema_path=self.schema_path)

        self._queue_darkness = queue.Queue()
        self.all_nodes_inactive = threading.Event()
        self.exhale_queue = ExhaleQueue(1, self)

        self.good_bye_with_nodes = threading.Event()

        self.nodes = []

    def start(self):
        '''\
        simulation 開始。
        simulation に必要な node thread を多数作成する。
        node thread 作成後、Client が leave_there を
        signal 状態にするまで待機し続ける。
        node が吐き出したqueueを、clientと共有するdbにcommitする。
        '''
        # create db in ExhaleQueue()
        self.exhale_queue.start()

        for i in range(self.num_nodes):
            id = self.first_node_id + i
            host, port = 'localhost', 10000 + id
            d_node = {
                'host': host, 'port': port, 'id': id,
                'start_up_time': self.start_up_time,
                'good_bye_with_darkness': self.good_bye_with_nodes,
                '_queue_darkness': self._queue_darkness
            }
            node_ = Node(**d_node)
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

        # 全てのnodeが不活性となった後、queueにobjを追加するnodeは存在しない。
        # また、不活性となった後、exhale_queue sched は自動的に停止する。
        self.all_nodes_inactive.set()
        # よって、ここより下でも上でも、inhole_queues_from_nodes()を
        # 実行する必要はない。
        # ただし、_queue_darkness内のqueueを取りこぼさないために、
        # client_db.close() を確実に実行させるために、
        # ExhaleQueue() 内の sched thread の終了を保証する必要がある。
        self.exhale_queue.join()

    def stop(self):
        '''simulation 終了'''
        for i in range(self.num_nodes):
            self.logger.info('stop node i={}'.format(i))

    def __str__(self):
        return 'Darkness(id={})'.format(self.id)
