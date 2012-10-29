import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lib import make_logger

class Darkness(object):
    '''漆黒の闇'''

    def __init__(self, db_dir, no, num_nodes, made_nodes, leave_there):
        self.db_dir = db_dir
        self.no = no
        self.num_nodes = num_nodes
        self.node_index = self.no * self.num_nodes
        self.made_nodes = made_nodes
        self.leave_there = leave_there # multiprocessing.Event()

        self.nodes = []
        self.len_nodes = 0

        self.logger = make_logger(self.db_dir, 'darkness', self.no)
        self.logger.info(('initilized Darkness(no={}, '
                                      'num_nodes={})').format(self.no, self.num_nodes))

    def start(self):
        for i in range(self.num_nodes):
            no = self.node_index + i
            self.logger.info('create node no={}'.format(no))
            self.nodes.append(no)

        self.made_nodes.value = len(self.nodes)
        msg = 'Darkness(no={}) made {} nodes.'.format(self.no, self.made_nodes.value)
        self.logger.info(msg)

        self.leave_there.wait()
        self.logger.info(('Darkness(no={}) got leave_there signal.').format(self.no))

    def stop(self):
        for i in range(self.num_nodes):
            self.logger.info('stop node i={}'.format(i))
