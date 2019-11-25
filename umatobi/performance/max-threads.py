# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import threading
import time
import _thread # for except _thread.error

class LimitedThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.die_out = False

    def run(self):
        while not self.die_out:
            time.sleep(0.01)

threads = []
for i in range(100000000):
    thread = LimitedThread()
    try:
        thread.start()
    except _thread.error as raiz:
      # print('raiz.args =', raiz.args)
        if raiz.args == ("can't start new thread",):
            break
    threads.append(thread)

# print('dir(threads[0]) =')
# print(dir(threads[0]))
print('len(threads) =', len(threads))
# help(threads[0])

for thread in threads:
    thread.die_out = True
    thread.join()
