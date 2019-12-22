# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import socket, random

from umatobi.log import *

ADDRESS_FAMILY = {
    'v4': socket.AF_INET,
    'v6': socket.AF_INET6,
# 'file': socket.AF_UNIX,
}

SOCKET_KIND = {
    'tcp': socket.SOCK_STREAM,
    'udp': socket.SOCK_DGRAM,
#   'raw': socket.SOCK_RAW,
}

def sock_create(v4_v6, tcp_udp):
    #  import socket;help(socket)

    #  AddressFamily(value, names=None, *, module=None, qualname=None, type=None, start=1)
    #  AF_INET = <AddressFamily.AF_INET: 2>
    #  AF_INET6 = <AddressFamily.AF_INET6: 30>
    #  AF_UNIX = <AddressFamily.AF_UNIX: 1>

    v4_v6 = v4_v6.lower()

    try:
        af = ADDRESS_FAMILY[v4_v6]
    except KeyError as err:
        if err.args[0] != v4_v6:
            raise err
        logger.error(f"\"{v4_v6}\" is inappropriate as v4_v6.")
        return None

    #  SocketKind(value, names=None, *, module=None, qualname=None, type=None, start=1)
    #  SOCK_DGRAM = <SocketKind.SOCK_DGRAM: 2>
    #  SOCK_STREAM = <SocketKind.SOCK_STREAM: 1>

    #  Data descriptors defined here:
    #  family
    #      the socket family
    #
    #  proto
    #      the socket protocol
    #
    #  timeout
    #      the socket timeout
    #
    #  type
    #      the socket type

    tcp_udp = tcp_udp.lower()

    try:
        sk = SOCKET_KIND[tcp_udp]
    except KeyError as err:
        if err.args[0] != tcp_udp:
            raise err
        logger.error(f"\"{tcp_udp}\" is inappropriate as tcp_udp.")
        return None

    sock = socket.socket(af, sk)

    return sock

def sock_make_addr(host, port):

    if host and port in range(1, 65535 + 1):
        return (host, port)

    return None

def sock_make(sock, host, port, v4_v6=None, tcp_udp=None):

    addr = sock_make_addr(host, port)
    if not addr:
        return None

    if not sock:
        sock = sock_create(v4_v6, tcp_udp)
        if not sock:
            return None

    return sock

def sock_bind(sock, host, port, v4_v6=None, tcp_udp=None):
    result = False

    addr = (host, port)

    if sock is None:
        sock = sock_create(v4_v6, tcp_udp)
        if sock is None:
            return (None, addr, result)

    error = None
    try:
        sock.bind(addr)
        result = True
    except socket.timeout as err:
        error = err
    except socket.error as err:
        if err.args in (
            (98, 'Address already in use',),
            (13, 'Permission denied',),
            ('getsockaddrarg: port must be 0-65535.',),
            ):
            pass
        else:
            raise err
        error = err
    except TypeError as err:
        if err.args in (
            ('str, bytes or bytearray expected, not NoneType',),
            ('an integer is required (got type NoneType)',),
            ):
            pass
        else:
            raise err
        error = err
    except OverflowError as err:
      # getsockaddrarg: port must be 0-65535.
        error = err

    if error:
        logger.error(f'cannot bind{addr}. reason={error.args}')

    return (sock, addr, result)

def sock_connect(sock, host, port, v4_v6=None, tcp_udp=None):

    addr = sock_make_addr(host, port)
    if not addr:
        return None

    if not sock:
        sock = sock_create(v4_v6, tcp_udp)
        if not sock:
            return None

    try:
        sock.connect(addr)
    except ConnectionRefusedError as err:
        # err.args[0] ==  61
        if err.args[1] == 'Connection refused':
            pass
        else:
            sock.close()
            raise err

    return sock

def sock_send(tcp_sock, data):
    try:
        result = tcp_sock.sendall(data)
    except socket.timeout as e:
        logger.info(f"{tcp_sock}.sendall() got timeout.")
        return False
    return True

def sock_recv(tcp_sock, buf_size):
    try:
        recved_data = tcp_sock.recv(buf_size)
    except socket.timeout:
        logger.info(f"{tcp_sock}.recv({buf_size}) got timeout.")
        recved_data = None

    return recved_data

def addr_on_localhost(addr):
    if addr[0] in ('localhost', '127.0.0.1'):
        logger.info(f'addr={addr} is on localhost.')
        return True
    else:
        logger.info(f'addr={addr} is not on localhost.')
        return False

def get_host_port(host_port):
    sp = host_port.split(':')
    host = sp[0]
    port = int(sp[1])
    return host, port

def bind_unused_port(sock, host, port_range, randomize=False):

    ports = [port for port in port_range]
    if randomize:
        random.shuffle(ports)

    for port in ports:
        addr = (host, port)

        try:
            # 以下で、bind() して帰ってくるので、
            # self.server_close() or sock.close() を忘れずに。
            sock.bind(addr)
        except OSError as oe:
          # Address already in use
            if oe.args[1] == 'Address already in use':
                continue
            else:
                raise(oe)
        return addr

    raise RuntimeError("all ports are in use.")

class StringTelephone(object):
    pass

if __name__ == '__main__':
    st = StringTelephone()
    print('st =', st)
    print('repr(st) =', repr(st))
  # st = 2019-10-20T13:09:26.307215
  # repr(st) = <__main__.SimulationTime object at 0x1083dd1d0>

    import umatobi
    print('umatobi.__path__ =', umatobi.__path__)
    import umatobi.lib
    print('umatobi.lib.__path__ =', umatobi.lib.__path__)
