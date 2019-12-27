# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import threading, pickle

from umatobi.log import *
from umatobi.lib.simulation_time import SimulationTime

class NodeCore(threading.Thread):
    '''NodeCore class'''

    TO_DARKNESS = {'id', 'count'}

    def __init__(self, id_, break_simulation, waked_up, queue_to_darkness):
        '''\
        node_core を初期化する。
        '''
        logger.info(f'NodeCore(id_={id_}) is created.')
        threading.Thread.__init__(self)
        # A break_simulation event is created by darkness.
        # darkness shares break_simulation with all nodes that is
        # create by a darkness.
        # A node set waked_up event to tell darkness that a node can
        # start simulation.
        self.id = id_
        self.break_simulation = break_simulation
        self.waked_up = waked_up
        self.queue_to_darkness = queue_to_darkness

        self.count = 0
        logger.info(f'NodeCore(id_={id_}) done.')

    def __str__(self):
        return f'NodeCore(id={self.id})'

    def get_attrs(self, attrs=None):
        if attrs is None:
            attrs = self.TO_DARKNESS

        return set(attrs)

    def load_queue_by_attrs(self, attrs):
        info = {}
        for attr in self.get_attrs(attrs):
            info[attr] = getattr(self, attr)
        tup = (SimulationTime(), info)
        pds = pickle.dumps(tup)

        self.queue_to_darkness.put(pds)

        return pds

    def run(self):
        self.waked_up.set()
        logger.info(f'{self} waked up.')
        got_attrs = self.get_attrs()
        self.load_queue_by_attrs(got_attrs)
        self.break_simulation.wait()
        logger.info(f'{self}.run() done.')

    # darkness awake node to run node.appear()
    def appear(self):
        logger.info(f'{self}.appear().')
        self.start()
        logger.info(f'{self}.appear() done.')

    # darkness set signal to break_simulation as do node.disappear()
    def disappear(self):
        logger.info(f'{self}.disappear().')
        self.break_simulation.set()
        self.join()
        logger.info(f'{self}.disappear() done.')
