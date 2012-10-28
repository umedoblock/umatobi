import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lib import make_logger

class Darkness(object):
    '''漆黒の闇'''

    def __init__(self, db_dir, no, num_nodes):
        self.db_dir = db_dir
        self.logger = make_logger(self.db_dir, 'darkness', no)
        self.logger.info('initilized Darkness(no={})'.format(no))
