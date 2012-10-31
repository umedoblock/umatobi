import sys, os
import threading

from . import node
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lib import make_logger

class Darkness(object):
    '''漆黒の闇'''

    def __init__(self, db_dir, no, num_nodes, first_node_no, made_nodes, leave_there):
        '''\
        Darkness process 内で 多数の node thread を作成する。
        Client が leave_there を signal 状態にしたら終了処理を行う。
        '''
        self.db_dir = db_dir
        self.no = no
        self.num_nodes = num_nodes
        self.made_nodes = made_nodes # multiprocessing.Value()
        self.leave_there = leave_there # multiprocessing.Event()

        self.good_bye_with_nodes = threading.Event()

        self.first_node_no = first_node_no

        self.nodes = []
        self.len_nodes = 0

        self.logger = make_logger(self.db_dir, 'darkness', self.no)
        self.logger.info(('initilized Darkness(no={}, '
                                      'num_nodes={})').format(self.no, self.num_nodes))

    def start(self):
        '''\
        simulation 開始。
        simulation に必要な node thread を多数作成する。
        node thread 作成後、Client が leave_there を
        signal 状態にするまで待機し続ける。
        '''
        for i in range(self.num_nodes):
            no = self.first_node_no + i
            self.logger.info('create node no={}'.format(no))
            node_ = node.Node('localhost', 10000 + no, no, self.good_bye_with_nodes)
            node_.start()
            self.nodes.append(node_)

        self.made_nodes.value = len(self.nodes)
        msg = 'Darkness(no={}) made {} nodes.'.format(self.no, self.made_nodes.value)
        self.logger.info(msg)

        self.leave_there.wait()
        self.logger.info(('Darkness(no={}) got leave_there signal.').format(self.no))
        self.logger.info(('Darkness(no={}) set good_bye_with_nodes signal.').format(self.no))
        self.good_bye_with_nodes.set()

        for node_ in self.nodes:
            node_.join()
            self.logger.info('node(no={}) thread joined.'.format(node_.no))

    def stop(self):
        '''simulation 終了'''
        for i in range(self.num_nodes):
            self.logger.info('stop node i={}'.format(i))
