import sys, os
import threading

from simulator.node import Node
from lib import make_logger

class Darkness(object):
    '''漆黒の闇'''

    def __init__(self, db_dir, id, num_nodes, first_node_id, made_nodes, leave_there):
        '''\
        Darkness process 内で 多数の node thread を作成する。
        Client が leave_there を signal 状態にしたら終了処理を行う。
        '''
        self.db_dir = db_dir
        self.id = id
        self.num_nodes = num_nodes
        self.made_nodes = made_nodes # multiprocessing.Value()
        self.leave_there = leave_there # multiprocessing.Event()

        self.good_bye_with_nodes = threading.Event()

        self.first_node_id = first_node_id

        self.nodes = []
        self.len_nodes = 0

        self.logger = make_logger(self.db_dir, 'darkness', self.id)
        self.logger.info(('{} initilized, '
                          'num_nodes={}.').format(self, self.num_nodes))
        self.logger.debug('{} debug log test.'.format(self))

    def start(self):
        '''\
        simulation 開始。
        simulation に必要な node thread を多数作成する。
        node thread 作成後、Client が leave_there を
        signal 状態にするまで待機し続ける。
        '''
        for i in range(self.num_nodes):
            id = self.first_node_id + i
            node_ = Node('localhost', 10000 + id, id, self.good_bye_with_nodes)
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

    def stop(self):
        '''simulation 終了'''
        for i in range(self.num_nodes):
            self.logger.info('stop node i={}'.format(i))

    def __str__(self):
        return 'Darkness(id={})'.format(self.id)
