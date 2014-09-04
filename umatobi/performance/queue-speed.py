import datetime
import threading
import queue
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lib.performance import stop_watch
from lib.performance import log_now

THREADS_NUM = 5
TIMES = 10 * 10000
TIMES = 10 * 100

class QueueRotate(threading.Thread):
    def __init__(self, queue_in, queue_out, times):
        threading.Thread.__init__(self)
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.times = times

    def run(self):
        for i in range(self.times):
            item = self.queue_in.get()
            self.queue_out.put(item)

def queue_rotation_performance(threads_num=THREADS_NUM, times=TIMES):
    threads = [None] * threads_num
    queues = [None] * threads_num

    for i in range(threads_num):
        queues[i] = queue.Queue()
    for i in range(threads_num):
        thread = \
            QueueRotate(queues[i%threads_num], queues[(i+1)%threads_num], \
                        times)
        thread.start()
        threads[i] = thread

    queues[0].put('rotation object')

    for thread in threads:
        thread.join()

    print('{} threads {} times rotate.'.format(len(threads), times))
    print('therefore put() and get() {} queues.'.format(threads_num * times))

class QueueConcentrateWorker(threading.Thread):
    def __init__(self, queue_concentrate, times, threads):
        threading.Thread.__init__(self)
        self.queue_concentrate = queue_concentrate
        self.times = times
        self.threads = threads
        self.len_threads = len(threads)

    def run(self):
        for i in range(self.times * self.len_threads):
            self.queue_concentrate.get()

class QueueConcentrate(threading.Thread):
    def __init__(self, queue_concentrate, times):
        threading.Thread.__init__(self)
        self.queue_concentrate = queue_concentrate
        self.times = times

    def run(self):
        for i in range(self.times):
            self.queue_concentrate.put(i)

def queue_concentrate_performance(threads_num=THREADS_NUM, times=TIMES):
    threads = [None] * threads_num
    queue_concentrate = queue.Queue()

    for i in range(threads_num):
        thread = QueueConcentrate(queue_concentrate, times)
        thread.start()
        threads[i] = thread

    worker = QueueConcentrateWorker(queue_concentrate, times, threads)
    worker.start()

    for thread in threads:
        thread.join()

    worker.join()

    print('{} threads {} times concentrate.'.format(len(threads), times))
    print('therefore put() and get() {} queues.'.format(threads_num * times))

if __name__ == "__main__":
    stop_watch(queue_rotation_performance)
    stop_watch(queue_concentrate_performance)
