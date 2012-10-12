import multiprocessing
import socket
import os
import threading
import time
import _thread # for except _thread.error

def make_many_udp_sockets():
    udp_sockets = []
  # for port in range(port_start, 65536):
  #     print('port =', port)
    while True:
#       socket.error: [Errno 24] Too many open files
        try:
            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as raiz:
          # print('raiz.args = "{}"'.format(raiz.args))
          # print('raiz = "{}"'.format(raiz))
            if raiz.args == (24, 'Too many open files'):
                break
            else:
                raise raiz
        udp_sockets.append(udp_sock)
    return udp_sockets

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

    udp_sockets = make_many_udp_sockets()
    print('no={}, len(udp_sockets) = {}'.format(no, len(udp_sockets)))
    print('no={}, len(threads) = {}'.format(no, len(threads)))
    print('no={}, created {} threads in a process(pid={}).'.format(no, len(threads), os.getpid()))
    print('no={}, id(state)=0x{:08x} in make_many_threads_in_process()'.format(no, id(state)))

    state.len_udp_sockets.value = len(udp_sockets)
    state.len_thread.value = len(threads)
    state.create_threads.set()

    print('no={} waiting... set leave_there to SIGNAL.'.format(state.no))
    state.leave_there.wait()
    state.init = 'cannot change in make_many_threads_in_process()'

    for thread in threads:
        thread.die_out.set()
        thread.join()

class State(object):
    def __init__(self, no, leave_there):
        self.no = no
        self.leave_there = leave_there # multiprocessing.Event()
        self.len_thread = multiprocessing.Value('i', 0)
        self.len_udp_sockets = multiprocessing.Value('i', 0)
        self.create_threads = multiprocessing.Event()
        self.init = 'in main'

if __name__ == '__main__':
    info('main line')
    ps = []
    states = []
    leave_there = multiprocessing.Event()
    total_threads = 0
    total_udp_sockets = 0

    for i in range(200):
        state = State(i, leave_there)
        print('no={}, id(state)=0x{:08x} in __main__'.format(state.no, id(state)))
        p = multiprocessing.Process(target=make_many_threads_in_process, args=(i, state))
        p.start()

        ps.append(p)
        state.create_threads.wait()
        total_threads += state.len_thread.value
        total_udp_sockets += state.len_udp_sockets.value
        states.append(state)
        if state.len_thread.value != 333:
            break

    for i, p in enumerate(ps):
        state = states[i]
        print('no={}, len_thread.value={}'.format(state.no, state.len_thread.value))
        print('no={}, len_udp_sockets.value={}'.format(state.no, state.len_udp_sockets.value))
        print('no={} state.init = {}.'.format(state.no, state.init))

    print('total_threads =', total_threads)
    print('total_udp_sockets =', total_udp_sockets)
  # time.sleep(30)

    leave_there.set()

    for i, p in enumerate(ps):
        p.join()
      # print('no={} prcess done.'.format(i))

    print()
