# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import sched, threading, time

from umatobi.log import *

class Polling(threading.Thread):

    @classmethod
    def sleep(cls, secs):
        logger.info(f'Polling.sleep(secs={secs})')
        time.sleep(secs)

    def __init__(self, polling_secs):
        threading.Thread.__init__(self)
        self.polling_secs = polling_secs
        self._sche = sched.scheduler(timefunc=time.time, delayfunc=Polling.sleep)
#       self._sche.enter(self.polling_secs, 1, self._polling, ()) # 犯人

    def polling(self):
        raise NotImplementedError()

    def is_continue(self):
        raise NotImplementedError()

    def _polling(self):
        if self.is_continue():
            self.polling()
            self._sche.enter(self.polling_secs, 1, self._polling, ())

    def run(self):
        self._sche.run()
