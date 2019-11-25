# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import threading
import datetime
import time
import socket
import sys
import struct
import argparse

def arg():
    parser = argparse.ArgumentParser(description='UDP sender/recver.')

    parser.add_argument('--recver', metavar='f', dest='recver',
                         nargs='?',
                         default='0.0.0.0:0',
                         help='example localhost:30000')
    parser.add_argument('--sender', metavar='f', dest='sender',
                         nargs='?',
                         default='0.0.0.0:0',
                         help='example localhost:20000')
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
    def __init__(self, sender, recver, type_, one_packet_size):
        threading.Thread.__init__(self)
        self.sender = sender
        self.recver = recver
        self.type_ = type_
        self.one_packet_size = one_packet_size
        self.s = None # datetime.datetime.now()
        self.timeout_sec = 4

        socket.setdefaulttimeout(self.timeout_sec)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if type_ == 'sender':
            self.sock.bind(sender)
        elif type_ == 'recver':
            self.sock.bind(recver)
        else:
            raise RuntimeError('unknown type: {}'.format(type_))

    def passed_time(self):
        e = datetime.datetime.now()
        return (e - self.s).total_seconds()

    def run(self):
        print("Start type_={}.".format(self.type_))

        hatena = (self.one_packet_size - 4) * b'?'
        count = 0
        total_send_size, total_recv_size = 0, 0

        passed_time = 0

        if self.type_ == 'sender':
            while True:
                print('\rcount={}'.format(count), end='')
                counter = struct.pack('>I', count)
                msg = counter + hatena
                if not self.s:
                    self.s = datetime.datetime.now()
                self.sock.sendto(msg, self.recver)
                count += 1
                total_send_size += len(msg)
                if self.passed_time() > 10:
                    break
        elif self.type_ == 'recver':
            sender = None
            recv_msg = b''
            try:
                while True:
                    print('\rcount={}'.format(count), end='')
                    recv_msg, sender = \
                        self.sock.recvfrom(self.one_packet_size)
                    if not self.s:
                        self.s = datetime.datetime.now()
                    count += 1
                    total_recv_size += len(recv_msg)
            except socket.timeout as raiz:
                if not count:
                    raise raiz
                elif sender:
                    self.sender = sender
                passed_time -= self.timeout_sec
        print()
        print('finished UDP sendto() successfully.')
        print()
        passed_time += self.passed_time()

        print('{}: count={:d}'.format(type_, count))
        print('passed_time={}'.format(passed_time))
        print()

        if self.type_ == 'sender':
            total_send_MB = total_send_size / 1024 ** 2
            print('total_send_size={}MB'.format(total_send_MB))
            print('speed is {:.3f}MB/s'.format(total_send_MB / passed_time))
            print('speed is {:.3f}Mbps/s'.format(total_send_MB / passed_time * 8))
        else:
            total_recv_MB = total_recv_size / 1024 ** 2
            print('total_recv_size={}MB'.format(total_recv_MB))
            print('speed is {:.3f}MB/s'.format(total_recv_MB / passed_time))
            print('speed is {:.3f}Mbps/s'.format(total_recv_MB / passed_time * 8))
        print()
        print('sender =', self.sender)
        print('recver =', self.recver)
        print("one_packet_size={}.".format(self.one_packet_size))

def get_host_port(host_port):
    sp = host_port.split(':')
    host = sp[0]
    port = int(sp[1])
    return host, port

if __name__ == '__main__':
    # how to use.
    # udp-speed.py --recver=localhost:30000 --type=recver
    # udp-speed.py --recver=localhost:30000 --type=sender

    args = arg()
    recver = get_host_port(args.recver)
    sender = get_host_port(args.sender)
    one_packet_size = args.one_packet_size
    type_ = args.type_

    if type_ not in ('sender', 'recver'):
        raise RuntimeError('--type is "{}", --type must be sender or recver.'.format(type_))

    node = \
        UDPNode(sender, recver, type_, one_packet_size)

    node.start()

    node.join()

    print('{} done.'.format(type_))
