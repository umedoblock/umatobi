# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import threading
import socket
import argparse

def arg():
    parser = argparse.ArgumentParser(description='TCP simple echo server.')

    parser.add_argument('--server', metavar='f', dest='server',
                         nargs='?',
                         default='0.0.0.0:0',
                         help='example localhost:20000')
    args = parser.parse_args()

    return args

class TCPserver(threading.Thread):
    def __init__(self, server):
        threading.Thread.__init__(self)
        self.server = server
        self.timeout_sec = 1
        self.n_clients = 4
        self.socks = []
asyncore.dispatcher_with_send
#       socket.setdefaulttimeout(self.timeout_sec)
        self.sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_server.bind(self.server)
        self.sock_server.listen(self.n_clients)
        print('self.server =', self.server)
        print('self.getsockname() =', self.sock_server.getsockname())

    def run(self):
        conn, addr = self.sock_server.accept()
        self.sock_server.sendto(send_msg, self.recver)
        server = self.sock_server.getsockname()
        print('cleint is {}.'.format(server))
        print('send to recver(={}) = {}'.format(self.recver, send_msg))

        recved_msg = ''
        recved_msg, who = self.sock_server.recvfrom(1024)

        print('who =', who)
        print('recved_msg =', recved_msg.decode())

def get_host_port(host_port):
    sp = host_port.split(':')
    host = sp[0]
    port = int(sp[1])
    return host, port

if __name__ == '__main__':
    # how to use.
    # tcp_server.py --recver=localhost:30000 \
    #               --server=localhost:20000 \
    #               --message='I am server.'

    args = arg()
    server_ = get_host_port(args.server)
    recver = get_host_port(args.recver)
    message = args.message.encode()

    server = TCPserver(server_, recver, message)
    server.do()


