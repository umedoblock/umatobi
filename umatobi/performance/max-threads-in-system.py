import multiprocessing
import os
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

def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())
    print()

def make_many_threads_in_process(no, state):
    info('make_many_threads_in_process(no={})'.format(no))

    threads = []
    for i in range(333):
        thread = LimitedThread()
        try:
            thread.start()
        except _thread.error as raiz:
            if raiz.args[0] == "can't start new thread":
                break
        threads.append(thread)

    print('no={}, len(threads) = {}'.format(no, len(threads)))
    print('no={}, created {} threads in a process(pid={}).'.format(no, len(threads), os.getpid()))
    print('no={}, id(state)=0x{:08x} in make_many_threads_in_process()'.format(no, id(state)))

  # created_thread_num = len(threads)
    state.len_thread.value = len(threads) * 1000 + state.no
    state.create_threads.set()

    state.leave_there.wait()
    state.init = 'in make_many_threads_in_process()'

    for thread in threads:
        thread.die_out = True
        thread.join()

class State(object):
    def __init__(self, no, leave_there):
        self.no = no
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

    for i in range(2):
        len_thread = multiprocessing.Value('i', 0)

        state = State(i, leave_there)
        print('no={}, id(state)=0x{:08x} in __main__'.format(state.no, id(state)))
        p = multiprocessing.Process(target=make_many_threads_in_process, args=(i, state))
        p.start()

        ps.append(p)
        states.append(state)

    leave_there.set()

    for i, p in enumerate(ps):
        states[i].create_threads.wait()
        print('no={}, len_thread.value={}'.format(states[i].no, states[i].len_thread.value))
        print('no={} state.init = {}.'.format(states[i].no, states[i].init))
        total_threads += states[i].len_thread.value

    for i, p in enumerate(ps):
        p.join()
        print('no={} prcess done.'.format(i))

    print()
    print('total_threads =', total_threads)
