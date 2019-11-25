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

def parse_args():
    parser = argparse.ArgumentParser(description='UDP sender/recver.')

    parser.add_argument('--wellknown-port', dest='wellknown_port',
                         action='store_true', default=False,
                         help='add well known ports')
    parser.add_argument('--ip', metavar='f', dest='ip',
                         nargs='?',
                         default='localhost',
                         help='example localhost')
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
        if type_ == 'sender':
            self.sock.bind(sender)
        elif type_ == 'recver':
            self.sock.bind(recver)
        else:
            raise RuntimeError('unknown type: {}'.format(type_))
        self.sock.sendto(msg, self.recver)

def get_host_port(host_port):
    sp = host_port.split(':')
    host = sp[0]
    port = int(sp[1])
    return host, port

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

if __name__ == '__main__':
    udp_sockets = make_many_udp_sockets()
    count_udp_sockets = len(udp_sockets)
    print('udp_sockets =', count_udp_sockets)
