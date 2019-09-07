import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

class Foo(object):
    sock = 'sock'

    def __init__(self):
        self.attr = 100
        self.sock = 'sock in __init__()'

    def sock2(self):
        pass

    def tes(self):
        return 'I am tes().'

if __name__ == '__main__':
    print('hello')
    m = MagicMock()
  # print('mock =', m)

    foo = Foo()
    with patch.object(foo, 'sock', 'sock with') as mocked:
        print('foo.sock =', foo.sock)

    with patch.object(foo, 'sock2', return_value='sock2() with') as mocked:
        print('foo.sock2() =', foo.sock2())

    foo3 = Foo()
    with patch.object(Foo, 'tes') as mocked_tes:
        mocked_tes.return_value = 'mocked_tes.return_value'
        print('foo3.tes() =', foo3.tes())
    print('go out from with')
    print('foo3.tes() =', foo3.tes())
