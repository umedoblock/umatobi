import threading
import datetime
import time
import socket
import sys
import struct
import argparse

def arg():
    parser = argparse.ArgumentParser(description='UDP simple client.')

    parser.add_argument('--client', metavar='f', dest='client',
                         nargs='?',
                         default='0.0.0.0:0',
                         help='example localhost:20000')
    parser.add_argument('--recver', metavar='f', dest='recver',
                         nargs='?',
                         default='0.0.0.0:0',
                         help='example localhost:30000')
    parser.add_argument('--message', metavar='f', dest='message',
                         nargs='?',
                         default='',
                         help='message')
    args = parser.parse_args()

    return args

class UDPClient(threading.Thread):
    def __init__(self, client, recver, message):
        threading.Thread.__init__(self)
        self.client = client
        self.recver = recver
        self.message = message
        self.timeout_sec = 1

        socket.setdefaulttimeout(self.timeout_sec)
        self.sock_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_client.bind(self.client)
        print('self.client =', self.client)
        print('self.getsockname() =', self.sock_client.getsockname())

    def do(self):
        send_msg = self.message
        self.sock_client.sendto(send_msg, self.recver)
        client = self.sock_client.getsockname()
        print('cleint is {}.'.format(client))
        print('send to recver(={}) = {}'.format(self.recver, send_msg))

        recved_msg = ''
        recved_msg, who = self.sock_client.recvfrom(1024)

        print('who =', who)
        print('recved_msg =', recved_msg.decode())

def get_host_port(host_port):
    sp = host_port.split(':')
    host = sp[0]
    port = int(sp[1])
    return host, port

if __name__ == '__main__':
    # how to use.
    # udp-client.py --recver=localhost:30000 \
    #               --client=localhost:20000 \
    #               --message='I am Client.'

    args = arg()
    client_ = get_host_port(args.client)
    recver = get_host_port(args.recver)
    message = args.message.encode()

    client = UDPClient(client_, recver, message)
    client.do()
