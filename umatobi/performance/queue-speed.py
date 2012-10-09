import datetime
import threading
import queue

from lib import stop_watch
from lib import log_now

threads_num = 5
times = 10 * 10000

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

def queue_rotation_performance():
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

stop_watch(queue_rotation_performance, 'queue_rotation_performance()')
