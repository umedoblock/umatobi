import socket

class Client(object):
    def __init__(self, watson_office_addr):
        self.watson_office_addr = watson_office_addr

    def _make_contact_with_raise(self):
        raise()

        self._tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._tcp_sock.connect(self.watson_office_addr)

    def _make_contact_with(self):
        self._tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._tcp_sock.connect(self.watson_office_addr)
