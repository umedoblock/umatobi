import threading
import datetime
import time
import socket
import sys
import struct
import argparse

def arg():
    parser = argparse.ArgumentParser(description='UDP sender/recver.')

    parser.add_argument('--recver-host', metavar='f', dest='recver_host',
                         nargs='?',
                         default='localhost',
                         help='my.server.net')
    parser.add_argument('--recver-port', metavar='f', dest='recver_port',
                         type=int, nargs='?',
                         default=10000,
                         help='recver port')
    parser.add_argument('--one-packet-size',
                         metavar='N', dest='one_packet_size',
                         type=int, nargs='?', default=(1024 * 4),
                         help='one packet size default is 4KO(4 * 1024)')
    parser.add_argument('--type', metavar='f', dest='type_',
                         nargs='?',
                         default='',
                         help='sender or recver')
    args = parser.parse_args()

    return args

class UDPNode(threading.Thread):
    def __init__(self, host, port, type_, one_packet_size):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.type_ = type_
        self.one_packet_size = one_packet_size
        self.s = None # datetime.datetime.today()
        self.timeout_sec = 4

        socket.setdefaulttimeout(self.timeout_sec)
        node = (host, port)
        print('node =', node)
        self.node = node
        if type_ == 'sender':
            self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        elif type_ == 'recver':
            self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.recv_sock.bind(node)
        else:
            raise RuntimeError('unknown type: {}'.format(type_))

    def passed_time(self):
        e = datetime.datetime.today()
        return (e - self.s).total_seconds()

    def run(self):
        print("Start host={}, port={}, type_={}.".
            format(self.host, self.port, self.type_))
        print("      one_packet_size={}.".format(self.one_packet_size))

        hatena = (self.one_packet_size - 4) * b'?'
        count = 0
        total_send_size, total_recv_size = 0, 0

        passed_time = 0
        try:
            while True:
                print('\rcount={}'.format(count), end='')
                if self.type_ == 'sender':
                    counter = struct.pack('>I', count)
                    msg = counter + hatena
                    if not self.s:
                        self.s = datetime.datetime.today()
                    self.send_sock.sendto(msg, self.node)
                    count += 1
                    total_send_size += len(msg)
                    if self.passed_time() > 10:
                        break
                elif type_ == 'recver':
                    recv_msg, sender = \
                        self.recv_sock.recvfrom(self.one_packet_size)
                    if not self.s:
                        self.s = datetime.datetime.today()
                    count += 1
                    total_recv_size += len(recv_msg)
        except socket.timeout:
            print('got a error as socket.timeout.')
            passed_time -= self.timeout_sec
        else:
            print('finished UDP sendto() successfully.')
        passed_time += self.passed_time()

        print('{}: count={:d}'.format(type_, count))
        print('passed_time={}'.format(passed_time))
        total_send_MB = total_send_size / 1024 ** 2
        total_recv_MB = total_recv_size / 1024 ** 2
        print('total_send_size={}MB'.format(total_send_MB))
        print('       speed is {}MB/s'.format(total_send_MB / passed_time))
        print('total_recv_size={}MB'.format(total_recv_MB))
        print('       speed is {}MB/s'.format(total_recv_MB / passed_time))

if __name__ == '__main__':
    # how to use.
    # udp-speed.py --recver-host=localhost --recver-port=30000 --type=recver
    # udp-speed.py --recver-host=localhost --recver-port=30000 --type=sender

    args = arg()
    recver_host = args.recver_host
    recver_port = int(args.recver_port)
    one_packet_size = args.one_packet_size
    type_ = args.type_

    if not type_:
        raise RuntimeError('--type must be sender or recver.')

    node = \
        UDPNode(recver_host, recver_port, type_, one_packet_size)

    node.start()

    node.join()

    print('{} done.'.format(type_))
