# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

# 16.3. multiprocessing — Process-based parallelism
# 16.3.1.1. The Process class

from multiprocessing import Process
import os
import time

def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())
    print()

def f(name):
    info('function f')
    print('hello', name)
    time.sleep(2000)

if __name__ == '__main__':
    info('main line')
    ps = []
    for i in range(100000000):
        p = Process(target=f, args=('bob',))
        p.start()
        ps.append(p)
        print('i =', i)
        if i > 100:
            break

    for i, p in enumerate(ps):
        p.join()
