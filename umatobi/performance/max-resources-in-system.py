# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import multiprocessing
import socket
import os
import sys
import threading
import time
import _thread # for except _thread.error

def make_many_udp_sockets():
    udp_sockets = []
  # for port in range(port_start, 65536):
  #     print('port =', port)
    while True:
        try:
            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as raiz:
          # print('raiz.args = "{}"'.format(raiz.args))
          # print('raiz = "{}"'.format(raiz))
            if raiz.args == (24, 'Too many open files') or \
               raiz.args == (23, 'Too many open files in system'):
               # 24: 1 process で作成できる udp socket の限界。
               # 23: system 全体で作成できる udp socket の限界。
#               print(raiz)
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
    print('process id:', os.getpid(), file=sys.stderr)
    print()

def make_many_threads_in_process(id, state):
  # info('make_many_threads_in_process(id={})'.format(id))

    threads = [None] * 333
  # for i in range(333):
  #     thread = LimitedThread()
  #     try:
  #         thread.start()
  #     except _thread.error as raiz:
  #         if raiz.args[0] == "can't start new thread":
  #             break
  #     threads.append(thread)

    udp_sockets = make_many_udp_sockets()
  # print('id={}, len(udp_sockets) = {}'.format(id, len(udp_sockets)), file=sys.stderr)
  # print('id={}, len(threads) = {}'.format(id, len(threads)))
  # print('id={}, created {} threads in a process(pid={}).'.format(id, len(threads), os.getpid()))
  # print('id={}, id(state)=0x{:08x} in make_many_threads_in_process()'.format(id, id(state)))

    state.len_udp_sockets.value = len(udp_sockets)
    state.len_thread.value = len(threads)
    state.create_threads.set()

  # print('id={} waiting... set leave_there to SIGNAL.'.format(state.id))
    state.leave_there.wait()
    state.init = 'cannot change in make_many_threads_in_process()'

  # for thread in threads:
  #     thread.die_out.set()
  #     thread.join()

class State(object):
    def __init__(self, id, leave_there):
        self.id = id
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

    first_len_thread = 0
    first_len_udp_sockets = 0
    for i in range(200):
        state = State(i, leave_there)
      # print('i =', i, file=sys.stderr)
      # print('id={}, id(state)=0x{:08x} in __main__'.format(state.id, id(state)))
        p = multiprocessing.Process(target=make_many_threads_in_process, args=(i, state))
        p.start()

        ps.append(p)
        state.create_threads.wait()
        total_threads += state.len_thread.value
        total_udp_sockets += state.len_udp_sockets.value

      # print('id={}, len_udp_sockets.value={}'.format(state.id, state.len_udp_sockets.value), file=sys.stderr)

        states.append(state)
        if first_len_udp_sockets == 0:
            first_len_udp_sockets = state.len_udp_sockets.value
        elif first_len_udp_sockets == state.len_udp_sockets.value:
            pass
        else:
            break
        if first_len_thread == 0:
            first_len_thread = state.len_thread.value
        elif first_len_thread == state.len_thread.value:
            pass
        else:
            break
    print('id={}, len_udp_sockets.value={}'.format(state.id, state.len_udp_sockets.value), file=sys.stderr)

  # for i, p in enumerate(ps):
  #     state = states[i]
  #     print('id={}, len_thread.value={}'.format(state.id, state.len_thread.value))
  #     print('id={} state.init = {}.'.format(state.id, state.init))

  # print('total_threads =', total_threads)
    print('total_udp_sockets =', total_udp_sockets)
  # time.sleep(30)

    leave_there.set()

    for i, p in enumerate(ps):
        p.join()
      # print('id={} prcess done.'.format(i))

    print()
