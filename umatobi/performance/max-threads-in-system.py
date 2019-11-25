# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import multiprocessing
import os
import threading
import time
import _thread # for except _thread.error

class LimitedThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.die_out = threading.Event()

    def run(self):
        self.die_out.wait()

def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())
    print()

def make_many_threads_in_process(id, state):
    info('make_many_threads_in_process(id={})'.format(id))

    threads = []
    for i in range(333):
        thread = LimitedThread()
        try:
            thread.start()
        except _thread.error as raiz:
            print('raiz.args =', raiz.args)
            if raiz.args == ("can't start new thread",):
                break
        threads.append(thread)

    print('id={}, len(threads) = {}'.format(id, len(threads)))
    print('id={}, created {} threads in a process(pid={}).'.format(id, len(threads), os.getpid()))
    print('id={}, id(state)=0x{:08x} in make_many_threads_in_process()'.format(id, id(state)))

    state.len_thread.value = len(threads)
    state.create_threads.set()

    print('id={} waiting... set leave_there to SIGNAL.'.format(state.id))
    state.leave_there.wait()
    state.init = 'cannot change in make_many_threads_in_process()'

    for thread in threads:
        thread.die_out.set()
        thread.join()

class State(object):
    def __init__(self, id, leave_there):
        self.id = id
        self.leave_there = leave_there # multiprocessing.Event()
        self.len_thread = multiprocessing.Value('i', 0)
        self.create_threads = multiprocessing.Event()
        self.init = 'in main'

if __name__ == '__main__':
    info('main line')
    ps = []
    states = []
    leave_there = multiprocessing.Event()
    total_threads = 0

    for i in range(200):
        state = State(i, leave_there)
        print('id={}, id(state)=0x{:08x} in __main__'.format(state.id, id(state)))
        p = multiprocessing.Process(target=make_many_threads_in_process, args=(i, state))
        p.start()

        ps.append(p)
        state.create_threads.wait()
        total_threads += state.len_thread.value
        states.append(state)
        if state.len_thread.value != 333:
            break

    for i, p in enumerate(ps):
        state = states[i]
        print('id={}, len_thread.value={}'.format(state.id, state.len_thread.value))
        print('id={} state.init = {}.'.format(state.id, state.init))

    print('total_threads =', total_threads)
  # time.sleep(30)

    leave_there.set()

    for i, p in enumerate(ps):
        p.join()
      # print('id={} prcess done.'.format(i))

    print()
