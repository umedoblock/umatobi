import multiprocessing
import socket
import os
import sys
import threading
import time
import _thread # for except _thread.error
import queue

class LimitedThread(threading.Thread):
    def __init__(self, queue_for_sql):
        threading.Thread.__init__(self)
        try:
            self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as raiz:
            if raiz.args == (24, 'Too many open files') or \
               raiz.args == (23, 'Too many open files in system'):
               print('LimitedThread reached limit.')
               raise raiz

        self.die_out = threading.Event()
        self.queue_for_sql = queue_for_sql

    def run(self):
        self.die_out.wait()

def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid(), file=sys.stderr)
    print()

def make_many_threads_in_process(id, state):
  # info('make_many_threads_in_process(id={})'.format(id))

    queue_for_sql = queue.Queue()
    threads = []
    for i in range(256):
        thread = LimitedThread(queue_for_sql)
        try:
            thread.start()
        except _thread.error as raiz:
            if raiz.args == ("can't start new thread",):
                break
        threads.append(thread)

    state.len_threads.value = len(threads)
    state.create_threads.set()

    state.leave_there.wait() # multiprocessing.Event()
    state.init = 'cannot change in make_many_threads_in_process()'

    for thread in threads:
        thread.die_out.set()
    for thread in threads:
        thread.join()

class State(object):
    def __init__(self, id, leave_there):
        self.id = id
        self.leave_there = leave_there # multiprocessing.Event()
        self.len_threads = multiprocessing.Value('i', 0)
        self.create_threads = multiprocessing.Event()
        self.init = 'in main'

if __name__ == '__main__':
    info('main line')
    ps = []
    states = []
    leave_there = multiprocessing.Event()
    total_threads = 0

    first_len_threads = 0
    for i in range(32):
        state = State(i, leave_there)
      # print('i =', i, file=sys.stderr)
      # print('id={}, id(state)=0x{:08x} in __main__'.format(state.id, id(state)))
        p = multiprocessing.Process(target=make_many_threads_in_process, args=(i, state))
        p.start()

        ps.append(p)
        state.create_threads.wait()
        total_threads += state.len_threads.value

        states.append(state)
        if first_len_threads == 0:
            first_len_threads = state.len_threads.value
        elif first_len_threads == state.len_threads.value:
            pass
        else:
            break

    print('total_threads =', total_threads)
  # time.sleep(30)

    leave_there.set() # multiprocessing.Event()

    for i, p in enumerate(ps):
        p.join()
      # print('id={} prcess done.'.format(i))

    print()
