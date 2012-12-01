import os
import sys
import time
import threading

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lib import Polling

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
