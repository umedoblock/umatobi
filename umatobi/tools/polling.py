# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import os
import sys
import time
import threading

from umatobi.lib import Polling

class PollingSample(Polling):
    def __init__(self, polling_secs):
        Polling.__init__(self, polling_secs)
        self.ev = threading.Event()
        self.count = 0

    def polling(self):
        print('count =', self.count)
        self.count += 1

    def is_continue(self):
        return not self.ev.is_set()

if __name__ == '__main__':
    pllsmp = PollingSample(0.1)
    pllsmp.start()
    time.sleep(2)
    pllsmp.ev.set()
    pllsmp.join()
